import os
import io
import uuid
import base64
from typing import Dict, List, Tuple, Optional
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, send_from_directory, send_file, jsonify
from functools import wraps
from PIL import Image
from ..core.forms_parser import (
    TORG12_FIELDS,
    torg12_make_string, torg12_parse_string,
    env_make_string, env_parse_string,
    exploitation_make_string, exploitation_parse_string,
    transport_make_string, transport_parse_string,
    custom_make_string, custom_parse_string,
    detect_form_by_prefix
)
from ..core.codes import generate_qr, generate_dm, save_image, generate_by_type
from ..models.history import add_history
import openpyxl

bp = Blueprint("forms", __name__)

def _save_and_maybe_log(img: Image.Image, text: str, code_type: str, form_type: Optional[str]) -> str:
    fname = f"{uuid.uuid4().hex}.png"
    fpath = os.path.join(current_app.config["STORAGE_CODES_DIR"], fname)
    save_image(img, fpath)
    if session.get("user"):
        add_history(session["user"]["id"], "created", code_type, form_type, text, fpath)
    return fname

@bp.route("/code/<path:filename>")
def code_image(filename: str):
    return send_from_directory(current_app.config["STORAGE_CODES_DIR"], filename, as_attachment=False)

# ----------------- CREATE (live) -----------------
@bp.route("/create", methods=["GET"])
def create_free():
    return render_template("form_create_live.html", title="Создать код")

@bp.route("/api_generate", methods=["POST"])
def api_generate_code():
    data = request.get_json(force=True, silent=True) or {}
    text = (data.get("text") or "").strip()
    code_type = data.get("code_type") or "QR"
    size = int(data.get("size") or 300)
    human_text = (data.get("human_text") or "").strip()
    gost_code = data.get("gost_code")
    if not text:
        return jsonify({"ok": False, "error": "Пустой текст"}), 400
    img = generate_by_type(code_type, text, size=size, human_text=human_text, gost_code=gost_code)
    bio = io.BytesIO()
    img.save(bio, format="PNG", optimize=True)
    b64 = base64.b64encode(bio.getvalue()).decode("ascii")
    return jsonify({"ok": True, "data_url": f"data:image/png;base64,{b64}"})

@bp.route("/api_save", methods=["POST"])
def api_save_code():
    text = (request.form.get("text") or "").strip()
    code_type = request.form.get("code_type") or "QR"
    size = int(request.form.get("size") or 300)
    gost_code = request.form.get("gost_code")
    fmt = (request.form.get("fmt") or "png").lower()
    if not text:
        flash("Пустой текст", "error")
        return redirect(url_for("forms.create_free"))

    img = generate_by_type(code_type, text, size=size, gost_code=gost_code)

    if session.get("user"):
        _ = _save_and_maybe_log(img, text, code_type, detect_form_by_prefix(text))

    out = io.BytesIO()
    download_name = f"code.{fmt}"
    if fmt == "jpg":
        rgb = img.convert("RGB")
        rgb.save(out, format="JPEG", quality=95, optimize=True)
    elif fmt == "pdf":
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.utils import ImageReader
            w, h = A4
            out_pdf = io.BytesIO()
            c = canvas.Canvas(out_pdf, pagesize=A4)
            bio = io.BytesIO(); img.save(bio, format="PNG"); bio.seek(0)
            iw, ih = img.size
            scale = min((w-72)/iw, (h-72)/ih)
            tw, th = iw*scale, ih*scale
            x = (w - tw)/2; y = (h - th)/2
            c.drawImage(ImageReader(bio), x, y, tw, th, mask='auto')
            c.showPage(); c.save()
            out_pdf.seek(0)
            out = out_pdf
        except Exception:
            img.save(out, format="PNG", optimize=True)
            download_name = "code.pdf"
    else:
        img.save(out, format="PNG", optimize=True)
        download_name = "code.png"

    out.seek(0)
    mimetype = "image/png" if fmt in ("png","pdf") else "image/jpeg"
    return send_file(out, as_attachment=True, download_name=download_name, mimetype=mimetype)

@bp.route("/api_save_history_copy", methods=["POST"])
def api_save_history_copy():
    data = request.get_json(force=True, silent=True) or {}
    data_url = data.get("data_url") or ""
    text = (data.get("text") or "").strip()
    code_type = data.get("code_type") or "QR"
    if not text or not data_url.startswith("data:image/"):
        return jsonify({"ok": False, "error": "Некорректные данные"}), 400
    try:
        head, b64 = data_url.split(",", 1)
        raw = base64.b64decode(b64)
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as e:
        return jsonify({"ok": False, "error": f"Не удалось разобрать изображение: {e}"}), 400

    form_type = detect_form_by_prefix(text)
    if session.get("user"):
        fname = f"{uuid.uuid4().hex}.png"
        fpath = os.path.join(current_app.config["STORAGE_CODES_DIR"], fname)
        save_image(img, fpath)
        add_history(session["user"]["id"], "created", code_type, form_type, text, fpath)
        return jsonify({"ok": True, "file": fname})
    return jsonify({"ok": True})

# ----------------- PREVIEW / ENCODE / IMPORT -----------------
@bp.route("/api_preview_table", methods=["POST"])
def api_preview_table():
    data = request.get_json(force=True, silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"ok": True, "form_type": None, "headers": [], "rows": []})
    f = detect_form_by_prefix(text)
    if f == "torg12":
        vals = torg12_parse_string(text)
        rows = [[code, label, vals.get(code, "")] for code, label in TORG12_FIELDS]
        return jsonify({"ok": True, "form_type": "torg12", "headers": ["Код","Наименование","Значение"], "rows": rows})
    if f == "message":
        rows = [[p, v] for p, v in env_parse_string(text)]
        return jsonify({"ok": True, "form_type": "message", "headers": ["Параметр","Значение"], "rows": rows})
    if f == "exploitation":
        rows = exploitation_parse_string(text)
        return jsonify({"ok": True, "form_type": "exploitation",
                        "headers": ["Обозначение СЧ","Входимость СЧ","Носитель маркировки","Серийный номер","Уникальный идентификатор"],
                        "rows": rows})
    if f == "transport":
        rows = transport_parse_string(text)
        return jsonify({"ok": True, "form_type": "transport",
                        "headers": ["Номер знака","Значение","Вид данных","Цифровое значение"],
                        "rows": rows})
    if f == "custom":
        rows = custom_parse_string(text)
        headers = [f"Колонка {i+1}" for i in range(max((len(r) for r in rows), default=0))]
        return jsonify({"ok": True, "form_type": "custom", "headers": headers, "rows": rows})
    return jsonify({"ok": True, "form_type": None, "headers": [], "rows": []})

@bp.route("/api_encode_table", methods=["POST"])
def api_encode_table():
    data = request.get_json(force=True, silent=True) or {}
    form_type = data.get("form_type")
    rows = data.get("rows") or []
    try:
        if form_type == "torg12":
            values: Dict[str, str] = {}
            for r in rows:
                if len(r) >= 3 and (r[0] or "").strip().isdigit() and len((r[0] or "").strip()) == 2:
                    values[(r[0] or "").strip()] = (r[2] or "").strip()
            return jsonify({"ok": True, "text": torg12_make_string(values)})
        if form_type == "message":
            pairs = []
            for r in rows:
                p = (r[0] or "").strip(); v = (r[1] or "").strip() if len(r) > 1 else ""
                pairs.append((p, v))
            return jsonify({"ok": True, "text": env_make_string(pairs)})
        if form_type == "exploitation":
            tup_rows = [tuple((c or "") for c in r + [""]*(5-len(r))) for r in rows]
            return jsonify({"ok": True, "text": exploitation_make_string(tup_rows)})  # type: ignore
        if form_type == "transport":
            tup_rows = [tuple((c or "") for c in r + [""]*(4-len(r))) for r in rows]
            return jsonify({"ok": True, "text": transport_make_string(tup_rows)})  # type: ignore
        if form_type == "custom":
            return jsonify({"ok": True, "text": custom_make_string(rows)})
        return jsonify({"ok": False, "error": "Неизвестная форма"}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@bp.route("/api_import_excel", methods=["POST"])
def api_import_excel():
    file = request.files.get("excel")
    if not file:
        return jsonify({"ok": False, "error": "Файл не выбран"}), 400
    try:
        wb = openpyxl.load_workbook(file)
        ws = wb.active
        values: Dict[str, str] = {}
        torg_hits = 0
        msg_hits  = 0
        exp_cols  = 0
        trn_cols  = 0
        rows_data: List[List[str]] = []
        for row in ws.iter_rows(values_only=True):
            if not row: continue
            row_vals = ["" if v is None else str(v).strip() for v in row]
            rows_data.append(row_vals)

            code = row_vals[0] if row_vals else ""
            if len(code) == 2 and code.isdigit():
                torg_hits += 1
                if len(row_vals) > 2: values[code] = row_vals[2]

            if len(row_vals) >= 2 and (row_vals[0] or row_vals[1]):
                msg_hits += 1

            exp_cols = max(exp_cols, len(row_vals))
            trn_cols = max(trn_cols, len(row_vals))

        if torg_hits >= 10:
            text = torg12_make_string(values)
            headers = ["Код","Наименование","Значение"]
            rows = [[code, label, values.get(code, "")] for code, label in TORG12_FIELDS]
            return jsonify({"ok": True, "form_type":"torg12", "text": text, "headers": headers, "rows": rows})

        if msg_hits >= 1 and exp_cols <= 3:
            pairs = []
            for r in rows_data:
                p = r[0] if len(r)>0 else ""
                v = r[1] if len(r)>1 else ""
                if p or v: pairs.append((p, v))
            text = env_make_string(pairs)
            return jsonify({"ok": True, "form_type":"message", "text": text, "headers":["Параметр","Значение"], "rows":[[p,v] for p,v in pairs]})

        if exp_cols >= 5:
            rows = [r[:5] + [""]*(5-len(r)) for r in rows_data if any(r)]
            text = exploitation_make_string([tuple(rr) for rr in rows])  # type: ignore
            return jsonify({"ok": True, "form_type":"exploitation", "text": text,
                            "headers":["Обозначение СЧ","Входимость СЧ","Носитель маркировки","Серийный номер","Уникальный идентификатор"],
                            "rows": rows})
        if trn_cols == 4:
            rows = [r[:4] + [""]*(4-len(r)) for r in rows_data if any(r)]
            text = transport_make_string([tuple(rr) for rr in rows])  # type: ignore
            return jsonify({"ok": True, "form_type":"transport", "text": text,
                            "headers":["Номер знака","Значение","Вид данных","Цифровое значение"],
                            "rows": rows})

        rows = [r for r in rows_data if any(r)]
        text = custom_make_string(rows)
        headers = [f"Колонка {i+1}" for i in range(max((len(r) for r in rows), default=0))]
        return jsonify({"ok": True, "form_type":"custom", "text": text, "headers": headers, "rows": rows})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Ошибка Excel: {e}"}), 500

# ----------------- FORMS PAGES -----------------
@bp.route("/torg12", methods=["GET", "POST"])
def form_torg12():
    initial: Dict[str, str] = {}
    q = request.args.get("q")
    if q:
        initial = torg12_parse_string(q)

    if request.method == "POST":
        code_type = request.form.get("code_type") or "QR"
        size = int(request.form.get("size") or 300)
        gost_code = request.form.get("gost_code")
        values: Dict[str, str] = {}
        for code, _label in TORG12_FIELDS:
            values[code] = (request.form.get(f"f_{code}") or "").strip()
        encoded = torg12_make_string(values)
        img = generate_by_type(code_type, encoded, size=size, gost_code=gost_code)
        fname = _save_and_maybe_log(img, encoded, (code_type or 'QR').upper(), "torg12")
        return render_template("form_torg12.html", title="ТОРГ-12",
                               fields=TORG12_FIELDS, initial=values, result_image=url_for("forms.code_image", filename=fname),
                               encoded=encoded, code_type=code_type, size=size, gost_code=gost_code)
    return render_template("form_torg12.html", title="ТОРГ-12", fields=TORG12_FIELDS, initial=initial)

@bp.route("/message", methods=["GET", "POST"])
def form_message():
    initial_pairs: List[Tuple[str, str]] = []
    q = request.args.get("q")
    if q:
        initial_pairs = env_parse_string(q)
    if request.method == "POST":
        code_type = request.form.get("code_type") or "QR"
        size = int(request.form.get("size") or 300)
        pairs: List[Tuple[str, str]] = []
        idx = 0
        while True:
            p = request.form.get(f"p_{idx}")
            v = request.form.get(f"v_{idx}")
            if p is None and v is None:
                break
            pairs.append((p or "", v or ""))
            idx += 1
        encoded = env_make_string(pairs)
        img = generate_by_type(code_type, encoded, size=size)
        fname = _save_and_maybe_log(img, encoded, (code_type or 'QR').upper(), "message")
        return render_template("form_message.html", title="Сообщение", pairs=pairs,
                               result_image=url_for("forms.code_image", filename=fname),
                               encoded=encoded, code_type=code_type, size=size)
    if not initial_pairs:
        initial_pairs = [("", "")]
    return render_template("form_message.html", title="Сообщение", pairs=initial_pairs)

@bp.route("/exploitation", methods=["GET", "POST"])
def form_exploitation():
    initial_rows: List[List[str]] = []
    q = request.args.get("q")
    if q:
        initial_rows = exploitation_parse_string(q)
    if request.method == "POST":
        code_type = request.form.get("code_type") or "QR"
        size = int(request.form.get("size") or 300)
        rows: List[List[str]] = []
        i = 0
        while True:
            marker = request.form.get(f"r{i}c0")
            if marker is None:
                break
            cols = []
            for c in range(5):
                cols.append(request.form.get(f"r{i}c{c}") or "")
            if all(v == "" for v in cols):
                break
            rows.append(cols)
            i += 1
        tup_rows = [tuple(r[:5]) for r in rows]
        encoded = exploitation_make_string(tup_rows)  # type: ignore
        img = generate_by_type(code_type, encoded, size=size)
        fname = _save_and_maybe_log(img, encoded, (code_type or 'QR').upper(), "exploitation")
        return render_template("form_exploitation.html", title="Эксплуатация", rows=rows,
                               result_image=url_for("forms.code_image", filename=fname),
                               encoded=encoded, code_type=code_type, size=size)
    if not initial_rows:
        initial_rows = [["", "", "", "", ""]]
    return render_template("form_exploitation.html", title="Эксплуатация", rows=initial_rows)

@bp.route("/transport", methods=["GET", "POST"])
def form_transport():
    initial_rows: List[List[str]] = []
    q = request.args.get("q")
    if q:
        initial_rows = transport_parse_string(q)
    if request.method == "POST":
        code_type = request.form.get("code_type") or "QR"
        size = int(request.form.get("size") or 300)
        rows: List[List[str]] = []
        i = 0
        while True:
            marker = request.form.get(f"r{i}c0")
            if marker is None:
                break
            cols = []
            for c in range(4):
                cols.append(request.form.get(f"r{i}c{c}") or "")
            if all(v == "" for v in cols):
                break
            rows.append(cols)
            i += 1
        tup_rows = [tuple(r[:4]) for r in rows]
        encoded = transport_make_string(tup_rows)  # type: ignore
        img = generate_by_type(code_type, encoded, size=size)
        fname = _save_and_maybe_log(img, encoded, (code_type or 'QR').upper(), "transport")
        return render_template("form_transport.html", title="Транспортная маркировка", rows=rows,
                               result_image=url_for("forms.code_image", filename=fname),
                               encoded=encoded, code_type=code_type, size=size)
    if not initial_rows:
        initial_rows = [["", "", "", ""]]
    return render_template("form_transport.html", title="Транспортная маркировка", rows=initial_rows)

@bp.route("/custom", methods=["GET", "POST"])
def form_custom():
    initial_rows: List[List[str]] = []
    q = request.args.get("q")
    if q:
        initial_rows = custom_parse_string(q)

    if request.method == "POST":
        code_type = request.form.get("code_type") or "QR"
        size = int(request.form.get("size") or 300)
        if (request.form.get("mode") or "table") == "table":
            rows: List[List[str]] = []
            i = 0
            while True:
                line = request.form.get(f"row_{i}")
                if line is None:
                    break
                parts = [c.strip() for c in (line or "").split("|")]
                rows.append(parts)
                i += 1
            encoded = custom_make_string(rows)
        else:
            encoded = (request.form.get("text") or "").strip()
        img = generate_by_type(code_type, encoded, size=size)
        fname = _save_and_maybe_log(img, encoded, (code_type or 'QR').upper(), "custom")
        return render_template("form_custom.html", title="Произвольная таблица/текст",
                               mode=request.form.get("mode") or "table",
                               rows=initial_rows, result_image=url_for("forms.code_image", filename=fname),
                               encoded=encoded, code_type=code_type, size=size)

    mode = request.args.get("mode") or "table"
    if mode == "free":
        return render_template("form_custom.html", title="Создать код (произвольно)", mode="free")
    if not initial_rows:
        initial_rows = [[""]]
    return render_template("form_custom.html", title="Произвольная таблица", mode="table", rows=initial_rows)