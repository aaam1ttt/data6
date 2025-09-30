import io
import os
import uuid
from typing import Optional

from flask import (
    Blueprint, render_template, request, redirect, url_for,
    flash, session, send_file, jsonify, current_app, send_from_directory
)
from functools import wraps
from PIL import Image
from werkzeug.exceptions import RequestEntityTooLarge

from ..core.codes import decode_auto, save_image
from ..core.forms_parser import (
    detect_form_by_prefix,
    TORG12_FIELDS, torg12_parse_string,
    env_parse_string, exploitation_parse_string,
    transport_parse_string, custom_parse_string,
)
from ..models.history import add_history
import openpyxl

bp = Blueprint("scan", __name__)

@bp.route("/", methods=["GET"])
def scan_page():
    user = session.get("user")
    return render_template("scan.html", title="Сканирование", user=user)

@bp.route("/upload/<path:filename>")
def upload_image(filename: str):
    return send_from_directory(current_app.config["STORAGE_UPLOADS_DIR"], filename, as_attachment=False)

@bp.route("/api", methods=["POST"])
def scan_api():
    file = request.files.get("image")
    if not file:
        return jsonify({"ok": False, "error": "Файл не получен"}), 400

    size_bytes = None
    try:
        pos = file.stream.tell()
        file.stream.seek(0, os.SEEK_END)
        size_bytes = file.stream.tell()
        file.stream.seek(pos)
    except Exception:
        pass
    if size_bytes is not None and size_bytes > 20 * 1024 * 1024:
        return jsonify({"ok": False, "error": "Файл больше 20 МБ"}), 413

    try:
        pil = Image.open(file.stream).convert("RGB")
    except Exception as e:
        return jsonify({"ok": False, "error": f"Не удалось открыть изображение: {e}"}), 400

    upload_fname = f"{uuid.uuid4().hex}.png"
    upload_path = os.path.join(current_app.config["STORAGE_UPLOADS_DIR"], upload_fname)
    upload_url = None
    try:
        save_image(pil, upload_path)
        upload_url = url_for("scan.upload_image", filename=upload_fname)
    except Exception:
        upload_path = None

    try:
        results = decode_auto(pil)
    except Exception as e:
        return jsonify({"ok": False, "error": f"Ошибка распознавания: {e}", "preview_url": upload_url}), 500

    if not results:
        return jsonify({"ok": False, "error": "Ошибка сканирования или код не найден", "preview_url": upload_url}), 200

    r = results[0]
    text = r["text"]
    code_type = r["type"]
    form_type = detect_form_by_prefix(text)

    if session.get("user"):
        add_history(session["user"]["id"], "scanned", code_type, form_type, text, upload_path)

    open_url: Optional[str] = None
    if form_type == "torg12":
        open_url = url_for("forms.form_torg12", q=text, from_scan="1")
    elif form_type == "message":
        open_url = url_for("forms.form_message", q=text, from_scan="1")
    elif form_type == "exploitation":
        open_url = url_for("forms.form_exploitation", q=text, from_scan="1")
    elif form_type == "transport":
        open_url = url_for("forms.form_transport", q=text, from_scan="1")
    elif form_type == "custom":
        open_url = url_for("forms.form_custom", q=text, mode="table", from_scan="1")

    return jsonify({
        "ok": True,
        "code_type": code_type,
        "form_type": form_type,
        "text": text,
        "open_url": open_url,
        "preview_url": upload_url
    })

@bp.app_errorhandler(RequestEntityTooLarge)
def too_large(e):
    if request.path.startswith("/scan/api"):
        return jsonify({"ok": False, "error": "Файл больше 20 МБ"}), 413
    flash("Файл больше 20 МБ", "error")
    return redirect(url_for("scan.scan_page"))

def _auto_adjust_column_widths(ws):
    """Автоматическая настройка ширины столбцов на основе содержимого"""
    for column_cells in ws.columns:
        max_length = 0
        column_letter = column_cells[0].column_letter
        
        for cell in column_cells:
            try:
                cell_value = str(cell.value) if cell.value is not None else ""
                if len(cell_value) > max_length:
                    max_length = len(cell_value)
            except:
                pass
        
        adjusted_width = min(max_length + 2, 100)
        ws.column_dimensions[column_letter].width = adjusted_width

@bp.route("/export_excel", methods=["POST"])
def export_excel():
    text = request.form.get("text") or ""
    form_type = request.form.get("form_type") or ""
    if not text or form_type not in {"torg12","message","exploitation","transport","custom"}:
        return jsonify({"ok": False, "error": "Нет табличной формы для экспорта"}), 400

    wb = openpyxl.Workbook()
    ws = wb.active

    if form_type == "torg12":
        ws.title = "ТОРГ-12"
        ws.append(["Код", "Наименование", "Значение"])
        values = torg12_parse_string(text)
        for code, label in TORG12_FIELDS:
            ws.append([code, label, values.get(code, "")])
        filename = "torg12.xlsx"
    elif form_type == "message":
        ws.title = "Сообщение"
        ws.append(["Параметр", "Значение"])
        for p, v in env_parse_string(text):
            ws.append([p, v])
        filename = "message.xlsx"
    elif form_type == "exploitation":
        ws.title = "Эксплуатация"
        ws.append(["Обозначение СЧ","Входимость СЧ","Носитель маркировки","Серийный номер","Уникальный идентификатор"])
        for row in exploitation_parse_string(text):
            ws.append(row)
        filename = "exploitation.xlsx"
    elif form_type == "transport":
        ws.title = "Транспорт"
        ws.append(["Номер знака","Значение","Вид данных","Цифровое значение"])
        for row in transport_parse_string(text):
            ws.append(row)
        filename = "transport.xlsx"
    else:
        ws.title = "Таблица"
        for row in custom_parse_string(text):
            ws.append(row)
        filename = "custom.xlsx"

    _auto_adjust_column_widths(ws)

    bio = io.BytesIO()
    wb.save(bio)
    bio.seek(0)
    return send_file(bio, as_attachment=True, download_name=filename,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")