from typing import List, Dict, Tuple, Optional

# Полный список полей ТОРГ-12 (55 строк)
TORG12_FIELDS: List[Tuple[str, str]] = [
    ("01", "Наименование организации-грузоотправителя"),
    ("02", "Код ОКПО организации-грузоотправителя"),
    ("03", "Адрес грузоотправителя"),
    ("04", "Телефон грузоотправителя"),
    ("05", "ИНН грузоотправителя"),
    ("06", "Расчётный счёт грузоотправителя"),
    ("07", "БИК грузоотправителя"),
    ("08", "Корреспондентский счёт грузоотправителя"),
    ("09", "Наименование организации-грузополучателя"),
    ("10", "Код ОКПО организации-грузополучателя"),
    ("11", "Адрес грузополучателя"),
    ("12", "Телефон грузополучателя"),
    ("13", "ИНН грузополучателя"),
    ("14", "Расчётный счёт грузополучателя"),
    ("15", "БИК грузополучателя"),
    ("16", "Корреспондентский счёт грузополучателя"),
    ("17", "Наименование организации-поставщика"),
    ("18", "Код ОКПО организации-поставщика"),
    ("19", "Адрес поставщика"),
    ("20", "Телефон поставщика"),
    ("21", "ИНН поставщика"),
    ("22", "Расчётный счёт поставщика"),
    ("23", "БИК поставщика"),
    ("24", "Корреспондентский счёт поставщика"),
    ("25", "Наименование организации-плательщика"),
    ("26", "Код ОКПО организации-плательщика"),
    ("27", "Адрес плательщика"),
    ("28", "Телефон плательщика"),
    ("29", "ИНН плательщика"),
    ("30", "Расчётный счёт плательщика"),
    ("31", "БИК плательщика"),
    ("32", "Корреспондентский счёт плательщика"),
    ("33", "Основание"),
    ("34", "Номер документа (накладной)"),
    ("35", "Дата составления документа (накладной)"),
    ("36", "Наименование, характеристика, сорт, артикул товара"),
    ("37", "Код товара"),
    ("38", "Единица измерения, наименование"),
    ("39", "Единица измерения, код по ОКЕИ"),
    ("40", "Вид упаковки"),
    ("41", "Количество товара в 1 месте"),
    ("42", "Количество мест, штук"),
    ("43", "Масса брутто, кг"),
    ("44", "Количество (масса нетто, кг)"),
    ("45", "Количество, штук"),
    ("46", "Цена, руб.коп"),
    ("47", "Сумма без учёта НДС, руб.коп"),
    ("48", "НДС, ставка %"),
    ("49", "НДС сумма, руб.коп"),
    ("50", "Сумма с учётом НДС, руб.коп"),
    ("51", "Категория"),
    ("52", "Дата изготовления"),
    ("53", "Дата окончания гарантийного срока"),
    ("54", "Серийный номер"),
    ("55", "ИНН организации-изготовителя"),
]

# --- Префиксы ---
PREFIX_TORG12 = "D>Rs06Gs1F//"
SUFFIX_TORG12 = "RsEoT"
PREFIX_MSG = "ENV>"
SUFFIX_MSG = "<ENV"
PREFIX_EXP = "EXP>"
SUFFIX_EXP = "<EXP"
PREFIX_TRN = "TRN>"
SUFFIX_TRN = "<TRN"
PREFIX_CUSTOM = "CUSTOM>"
SUFFIX_CUSTOM = "<CUSTOM"

def detect_form_by_prefix(text: str) -> Optional[str]:
    if not text:
        return None
    if text.startswith(PREFIX_TORG12) and text.endswith(SUFFIX_TORG12):
        return "torg12"
    if text.startswith(PREFIX_MSG) and text.endswith(SUFFIX_MSG):
        return "message"
    if text.startswith(PREFIX_EXP) and text.endswith(SUFFIX_EXP):
        return "exploitation"
    if text.startswith(PREFIX_TRN) and text.endswith(SUFFIX_TRN):
        return "transport"
    if text.startswith(PREFIX_CUSTOM) and text.endswith(SUFFIX_CUSTOM):
        return "custom"
    return None

# --- TORG12 ---
def torg12_make_string(values_by_code: Dict[str, str]) -> str:
    parts: List[str] = [PREFIX_TORG12]
    first = True
    for code, _ in TORG12_FIELDS:
        val = (values_by_code.get(code) or "").strip()
        if first:
            parts.append(f"{code}{val}")
            first = False
        else:
            parts.append(f"Gs{code}{val}")
    parts.append(SUFFIX_TORG12)
    return "".join(parts)

def torg12_parse_string(s: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if s.startswith(PREFIX_TORG12):
        s = s[len(PREFIX_TORG12):]
    if s.endswith(SUFFIX_TORG12):
        s = s[: -len(SUFFIX_TORG12)]
    chunks = s.split("Gs")
    for ch in chunks:
        if len(ch) >= 2:
            code = ch[:2]
            val = ch[2:]
            out[code] = val
    return out

# --- Message ENVELOPE ---
def env_make_string(pairs: List[Tuple[str, str]]) -> str:

    chunks = []
    for p, v in pairs:
        p = (p or "").strip()
        v = (v or "").strip()
        if p or v:
            chunks.append(f"{p}:{v}")
    return f"{PREFIX_MSG}{'/'.join(chunks)}{SUFFIX_MSG}"

def env_parse_string(s: str) -> List[Tuple[str, str]]:
    if s.startswith(PREFIX_MSG):
        s = s[len(PREFIX_MSG):]
    if s.endswith(SUFFIX_MSG):
        s = s[: -len(SUFFIX_MSG)]
    out: List[Tuple[str, str]] = []
    for part in s.split("/"):
        if not part:
            continue
        if ":" in part:
            p, v = part.split(":", 1)
        else:
            p, v = part, ""
        out.append((p, v))
    return out

# --- Exploitation (5 столбцов, строки через "/") ---
def exploitation_make_string(rows: List[Tuple[str, str, str, str, str]]) -> str:
    row_str = []
    for r in rows:
        cols = [c or "" for c in r]
        row_str.append("|".join(cols))
    return f"{PREFIX_EXP}{'/'.join(row_str)}{SUFFIX_EXP}"

def exploitation_parse_string(s: str) -> List[List[str]]:
    if s.startswith(PREFIX_EXP):
        s = s[len(PREFIX_EXP):]
    if s.endswith(SUFFIX_EXP):
        s = s[: -len(SUFFIX_EXP)]
    out: List[List[str]] = []
    for row in s.split("/"):
        if not row:
            continue
        out.append(row.split("|"))
    return out

# --- Transport (4 столбца) ---
def transport_make_string(rows: List[Tuple[str, str, str, str]]) -> str:
    row_str = []
    for r in rows:
        cols = [c or "" for c in r]
        row_str.append("|".join(cols))
    return f"{PREFIX_TRN}{'/'.join(row_str)}{SUFFIX_TRN}"

def transport_parse_string(s: str) -> List[List[str]]:
    if s.startswith(PREFIX_TRN):
        s = s[len(PREFIX_TRN):]
    if s.endswith(SUFFIX_TRN):
        s = s[: -len(SUFFIX_TRN)]
    out: List[List[str]] = []
    for row in s.split("/"):
        if not row:
            continue
        out.append(row.split("|"))
    return out

# --- Custom (произвольная таблица; строки через \n, ячейки через |) ---
def custom_make_string(rows: List[List[str]]) -> str:
    lines = ["|".join([c or "" for c in r]) for r in rows if any((c or "").strip() for c in r)]
    return f"{PREFIX_CUSTOM}" + "\n".join(lines) + f"{SUFFIX_CUSTOM}"

def custom_parse_string(s: str) -> List[List[str]]:
    if s.startswith(PREFIX_CUSTOM):
        s = s[len(PREFIX_CUSTOM):]
    if s.endswith(SUFFIX_CUSTOM):
        s = s[: -len(SUFFIX_CUSTOM)]
    out: List[List[str]] = []
    for line in s.splitlines():
        if not line.strip():
            continue
        out.append(line.split("|"))
    return out