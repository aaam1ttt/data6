"""
GOST-compliant barcode dimensions module.
Implements standardized barcode sizing according to Russian State Standards (GOST).
Based on GOST R 51294.1-2005 for automatic identification and data capture techniques.
"""

from typing import Dict, List, NamedTuple
import math

class GostDimension(NamedTuple):
    """GOST-compliant dimension specification"""
    code: str          # ГОСТ код размера
    name_ru: str       # Русское название
    name_en: str       # English name
    mm_width: float    # Ширина в мм
    mm_height: float   # Высота в мм
    pixels_72dpi: int  # Пиксели при 72 DPI
    pixels_150dpi: int # Пиксели при 150 DPI  
    pixels_300dpi: int # Пиксели при 300 DPI
    print_density: float # Плотность печати (точек/мм)

# ГОСТ Р 51294.1-2005 - стандартные размеры для штрих-кодов
# Основано на международных стандартах ISO/IEC с адаптацией для российских форм
GOST_BARCODE_DIMENSIONS: Dict[str, List[GostDimension]] = {
    # QR-коды по ГОСТ Р ИСО/МЭК 18004
    "QR": [
        GostDimension("QR-S1", "Малый (документооборот)", "Small (document flow)", 
                     15.0, 15.0, 42, 89, 177, 11.8),
        GostDimension("QR-S2", "Стандартный (ТОРГ-12)", "Standard (Torg-12)", 
                     20.0, 20.0, 57, 118, 236, 11.8),
        GostDimension("QR-S3", "Увеличенный (накладные)", "Large (invoices)", 
                     25.0, 25.0, 71, 148, 295, 11.8),
        GostDimension("QR-S4", "Печатный (этикетки)", "Print (labels)", 
                     30.0, 30.0, 85, 177, 354, 11.8),
    ],
    
    # DataMatrix по ГОСТ Р ИСО/МЭК 16022
    "DM": [
        GostDimension("DM-S1", "Микро (маркировка)", "Micro (marking)", 
                     8.0, 8.0, 23, 47, 94, 11.8),
        GostDimension("DM-S2", "Малый (детали)", "Small (parts)", 
                     12.0, 12.0, 34, 71, 142, 11.8),
        GostDimension("DM-S3", "Средний (упаковка)", "Medium (packaging)", 
                     16.0, 16.0, 45, 94, 189, 11.8),
        GostDimension("DM-S4", "Большой (паллеты)", "Large (pallets)", 
                     20.0, 20.0, 57, 118, 236, 11.8),
    ],
    
    # Code 128 по ГОСТ Р 51294.2-99
    "C128": [
        GostDimension("C128-H1", "Низкий (документы)", "Low (documents)", 
                     30.0, 8.0, 85, 177, 354, 11.8),
        GostDimension("C128-H2", "Средний (накладные)", "Medium (invoices)", 
                     40.0, 12.0, 113, 236, 472, 11.8),
        GostDimension("C128-H3", "Высокий (этикетки)", "High (labels)", 
                     50.0, 15.0, 142, 295, 590, 11.8),
        GostDimension("C128-H4", "Печатный (промышл.)", "Print (industrial)", 
                     60.0, 20.0, 170, 354, 708, 11.8),
    ],
    
    # PDF417 по ГОСТ Р ИСО/МЭК 15438
    "PDF417": [
        GostDimension("PDF417-S1", "Компактный (формы)", "Compact (forms)", 
                     25.0, 10.0, 71, 148, 295, 11.8),
        GostDimension("PDF417-S2", "Стандартный (документы)", "Standard (documents)", 
                     35.0, 15.0, 99, 207, 413, 11.8),
        GostDimension("PDF417-S3", "Расширенный (этикетки)", "Extended (labels)", 
                     45.0, 20.0, 128, 265, 531, 11.8),
        GostDimension("PDF417-S4", "Полный (промышленность)", "Full (industrial)", 
                     55.0, 25.0, 156, 325, 649, 11.8),
    ],
    
    # Aztec по стандарту ГОСТ (аналог ISO/IEC 24778)
    "AZTEC": [
        GostDimension("AZ-S1", "Малый (документооборот)", "Small (document flow)", 
                     15.0, 15.0, 42, 89, 177, 11.8),
        GostDimension("AZ-S2", "Средний (формы)", "Medium (forms)", 
                     20.0, 20.0, 57, 118, 236, 11.8),
        GostDimension("AZ-S3", "Большой (этикетки)", "Large (labels)", 
                     25.0, 25.0, 71, 148, 295, 11.8),
        GostDimension("AZ-S4", "Печатный (промышл.)", "Print (industrial)", 
                     30.0, 30.0, 85, 177, 354, 11.8),
    ]
}

def get_gost_dimensions(code_type: str) -> List[GostDimension]:
    """Получить ГОСТ размеры для типа штрих-кода"""
    return GOST_BARCODE_DIMENSIONS.get(code_type.upper(), GOST_BARCODE_DIMENSIONS["QR"])

def get_dimension_by_code(gost_code: str) -> GostDimension:
    """Найти размер по ГОСТ коду"""
    for dimensions in GOST_BARCODE_DIMENSIONS.values():
        for dim in dimensions:
            if dim.code == gost_code:
                return dim
    raise ValueError(f"ГОСТ код {gost_code} не найден")

def calculate_print_layout(page_width_mm: float, page_height_mm: float, 
                         barcode_width_mm: float, barcode_height_mm: float,
                         margin_mm: float = 5.0) -> tuple[int, int, int]:
    """
    Вычисляет количество штрих-кодов, помещающихся на страницу.
    
    Args:
        page_width_mm: Ширина страницы в мм
        page_height_mm: Высота страницы в мм
        barcode_width_mm: Ширина штрих-кода в мм
        barcode_height_mm: Высота штрих-кода в мм
        margin_mm: Отступ от краев в мм
    
    Returns:
        tuple: (кодов_по_горизонтали, кодов_по_вертикали, всего_кодов)
    """
    # Доступная площадь с учетом отступов
    available_width = page_width_mm - (2 * margin_mm)
    available_height = page_height_mm - (2 * margin_mm)
    
    # Количество кодов с учетом промежутков между ними
    codes_horizontal = max(1, int(available_width // (barcode_width_mm + 2)))
    codes_vertical = max(1, int(available_height // (barcode_height_mm + 2)))
    
    total_codes = codes_horizontal * codes_vertical
    
    return codes_horizontal, codes_vertical, total_codes

def get_a4_layout_info(dimension: GostDimension) -> Dict[str, any]:
    """Получить информацию о размещении на листе А4"""
    # А4: 210 x 297 мм
    h_count, v_count, total = calculate_print_layout(210, 297, 
                                                   dimension.mm_width, 
                                                   dimension.mm_height)
    
    return {
        'horizontal_count': h_count,
        'vertical_count': v_count,
        'total_per_page': total,
        'page_format': 'A4 (210×297 мм)',
        'usage_efficiency': round((total * dimension.mm_width * dimension.mm_height) / (210 * 297) * 100, 1)
    }

def get_legacy_pixel_size(dimension: GostDimension, target_dpi: int = 300) -> int:
    """
    Преобразует ГОСТ размер в пиксели для совместимости с существующим кодом.
    Возвращает размер стороны квадрата для квадратных кодов или высоту для линейных.
    """
    if target_dpi == 72:
        base_pixels = dimension.pixels_72dpi
    elif target_dpi == 150:
        base_pixels = dimension.pixels_150dpi
    elif target_dpi == 300:
        base_pixels = dimension.pixels_300dpi
    else:
        # Расчет для произвольного DPI
        base_pixels = int(max(dimension.mm_width, dimension.mm_height) * target_dpi / 25.4)
    
    if dimension.mm_width == dimension.mm_height:
        return base_pixels
    else:
        return int(dimension.mm_height * target_dpi / 25.4)

LEGACY_TO_GOST_MAPPING = {
    300: "QR-S4",
    420: "QR-S4",
    600: "QR-S4",
    280: "DM-S4",    # Старый "стандарт" -> ГОСТ большой
    360: "DM-S4",    # Соответствует
    520: "DM-S4",    # Большой размер
    
    # Code 128
    200: "C128-H2",  # Старая высота -> ГОСТ средний
    280: "C128-H3",  # Соответствует высокому
    360: "C128-H4",  # Печатный размер
    
    # PDF417 (аналогично Code128)
    200: "PDF417-S2",
    280: "PDF417-S3", 
    360: "PDF417-S4"
}

def migrate_legacy_size(old_pixel_size: int, code_type: str) -> str:
    """Преобразует старый размер в пикселях в ГОСТ код"""
    gost_code = LEGACY_TO_GOST_MAPPING.get(old_pixel_size)
    if gost_code and gost_code.startswith(code_type.upper()):
        return gost_code
    
    # Если прямого соответствия нет, найдем ближайший ГОСТ размер
    dimensions = get_gost_dimensions(code_type)
    best_match = dimensions[0]  # По умолчанию первый
    min_diff = float('inf')
    
    for dim in dimensions:
        pixel_size = get_legacy_pixel_size(dim)
        diff = abs(pixel_size - old_pixel_size)
        if diff < min_diff:
            min_diff = diff
            best_match = dim
    
    return best_match.code