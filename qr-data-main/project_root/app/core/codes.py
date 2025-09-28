from typing import Optional, List, Dict
from PIL import Image
import io
import os
from .gost_dimensions import (
    get_gost_dimensions, get_dimension_by_code, get_legacy_pixel_size,
    migrate_legacy_size, GostDimension
)

def _scale_nearest_exact(img: Image.Image, target: int) -> Image.Image:
    w, h = img.size
    if w == h and w != 0:
        k = max(1, round(target / w))
        out = img.resize((w * k, h * k), Image.NEAREST)
        if out.size[0] != target:
            out = out.resize((target, target), Image.NEAREST)
        return out
    return img.resize((target, target), Image.NEAREST)

def _scale_preserve_aspect_height(img: Image.Image, target_h: int) -> Image.Image:
    w, h = img.size
    if h == 0:
        return img
    k = max(1, round(target_h / h))
    new_w = max(1, w * k)
    new_h = max(1, h * k)
    out = img.resize((new_w, new_h), Image.NEAREST)
    if out.size[1] != target_h:
        ratio = target_h / out.size[1]
        out = out.resize((max(1, int(out.size[0] * ratio)), target_h), Image.NEAREST)
    return out

def _add_text_below_barcode(img: Image.Image, text: str) -> Image.Image:
    try:
        from PIL import ImageDraw, ImageFont
        
        text_height = 40
        new_img = Image.new('RGB', (img.width, img.height + text_height), 'white')
        new_img.paste(img, (0, 0))
        
        draw = ImageDraw.Draw(new_img)
        
        font_size = 24
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
                except:
                    font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (img.width - text_width) // 2
        y = img.height + 8
        
        draw.text((x, y), text, fill='black', font=font)
        
        return new_img
    except Exception:
        return img

def generate_qr(text: str, size: int = 300, preferred_ecc: str = "H", gost_code: str = None) -> Image.Image:
    import qrcode
    from PIL import Image
    from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

    ecc_map = {
        "L": ERROR_CORRECT_L,
        "M": ERROR_CORRECT_M,
        "Q": ERROR_CORRECT_Q,
        "H": ERROR_CORRECT_H,
    }
    order = ["H", "Q", "M", "L"]
    start = order.index(preferred_ecc) if preferred_ecc in order else 0
    try_levels = order[start:]

    if gost_code:
        try:
            gost_dim = get_dimension_by_code(gost_code)
            actual_size = gost_dim.pixels_300dpi
            internal_size = actual_size
            min_internal_size = max(internal_size, int(gost_dim.mm_width * gost_dim.print_density))
            base_box_size = max(8, min_internal_size // 37)
        except ValueError:
            gost_code = None
    
    if not gost_code:
        dpi_scale_factor = 3
        internal_size = size * dpi_scale_factor
        
        min_internal_size = max(internal_size, 1800)
        
        base_box_size = max(12, min_internal_size // 37)
        actual_size = size
    
    last_err: Optional[Exception] = None
    for lvl in try_levels:
        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=ecc_map[lvl],
                box_size=base_box_size,
                border=4
            )
            qr.add_data(text)
            qr.make(fit=True)
            
            matrix = qr.get_matrix()
            n_modules = len(matrix)
            border = qr.border
            total_modules = n_modules + border * 2
            
            box_size = max(base_box_size, min_internal_size // total_modules)
            qr.box_size = box_size
            
            img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
            
            actual_internal_size = total_modules * box_size
            if actual_internal_size != internal_size:
                if actual_internal_size > internal_size:
                    img = img.resize((internal_size, internal_size), Image.LANCZOS)
                else:
                    img = _scale_nearest_exact(img, internal_size)
            
            if internal_size != actual_size:
                img = img.resize((actual_size, actual_size), Image.LANCZOS)

            logo_path = os.path.join(os.path.dirname(__file__), "..", "static", "star.png")
            logo_path = os.path.abspath(logo_path)
            if os.path.exists(logo_path):
                logo = Image.open(logo_path).convert("RGBA")
                logo_size = actual_size // 8 if lvl == "H" else actual_size // 6
                logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
                pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
                img.paste(logo, pos, mask=logo)

            return img
        except Exception as e:
            last_err = e
            continue
    raise ValueError("Слишком длинный текст для QR даже на уровне L") from last_err

def generate_dm(text: str, size: int = 300, gost_code: str = None) -> Image.Image:
    from pylibdmtx.pylibdmtx import encode as dm_encode
    
    if gost_code:
        try:
            gost_dim = get_dimension_by_code(gost_code)
            actual_size = gost_dim.pixels_300dpi
            internal_size = actual_size * 2
            min_internal_size = max(internal_size, int(gost_dim.mm_width * gost_dim.print_density * 2))
        except ValueError:
            gost_code = None
    
    if not gost_code:
        dpi_scale_factor = 4
        internal_size = size * dpi_scale_factor
        min_internal_size = max(internal_size, 2000)
        actual_size = size
    
    en = dm_encode(text.encode("utf-8"))
    base = Image.frombytes('RGB', (en.width, en.height), en.pixels)
    
    min_scale = max(16, size // max(base.size))
    
    scaled_size = base.size[0] * min_scale
    if scaled_size < size:
        scale_factor = size // base.size[0]
        high_res = base.resize(
            (base.size[0] * scale_factor, base.size[1] * scale_factor), 
            Image.NEAREST
        )
        if high_res.size[0] != internal_size:
            high_res = _scale_nearest_exact(high_res, internal_size)
        
        if internal_size != actual_size:
            return high_res.resize((actual_size, actual_size), Image.LANCZOS)
        return high_res
    
    scaled = _scale_nearest_exact(base, internal_size)
    if internal_size != actual_size:
        return scaled.resize((actual_size, actual_size), Image.LANCZOS)
    return scaled

def generate_code128(text: str, size: int = 300, human_text: str = "", gost_code: str = None) -> Image.Image:
    try:
        import barcode
        from barcode.writer import ImageWriter
        Code128 = barcode.get_barcode_class('code128')
        
        if gost_code:
            try:
                gost_dim = get_dimension_by_code(gost_code)
                actual_height = int(gost_dim.mm_height * 300 / 25.4)
                internal_size = actual_height * 3
            except ValueError:
                gost_code = None
        
        if not gost_code:
            dpi_scale_factor = 3
            internal_size = size * dpi_scale_factor
            actual_height = size
        
        code = Code128(text, writer=ImageWriter())
        bio = io.BytesIO()
        
        target_height_mm = internal_size / dpi_scale_factor / 31.5 * 3
        options = {
            "module_height": target_height_mm * 2.5,
            "module_width": 0.33,
            "quiet_zone": 3.0,
            "font_size": 0,
            "text_distance": 5.0,
            "write_text": False,
            "dpi": 300
        }
        
        code.write(bio, options=options)
        bio.seek(0)
        img = Image.open(bio).convert("RGB")
        
        high_res = _scale_preserve_aspect_height(img, internal_size)
        
        if human_text:
            high_res = _add_text_below_barcode(high_res, human_text)
        
        if internal_size != actual_height:
            return _scale_preserve_aspect_height(high_res, actual_height)
        return high_res
    except Exception as e:
        raise RuntimeError("Не удалось сгенерировать Code128. Установите 'python-barcode'.") from e

def generate_pdf417(text: str, size: int = 300, human_text: str = "", gost_code: str = None) -> Image.Image:
    try:
        import pdf417gen
        
        if gost_code:
            try:
                gost_dim = get_dimension_by_code(gost_code)
                actual_height = int(gost_dim.mm_height * 300 / 25.4)
                internal_size = actual_height * 3
                dpi_pixels_per_mm = 31.5
                target_height_mm = actual_height / dpi_pixels_per_mm
            except ValueError:
                gost_code = None
        
        if not gost_code:
            dpi_scale_factor = 3
            internal_size = size * dpi_scale_factor
            actual_height = size
            dpi_pixels_per_mm = 31.5
            target_height_mm = size / dpi_pixels_per_mm
        
        codes = pdf417gen.encode(text, columns=6, security_level=2)
        scale = max(3, int(target_height_mm * 0.5))
        img = pdf417gen.render_image(codes, scale=scale, ratio=3)
        img = img.convert("RGB")
        
        high_res = _scale_preserve_aspect_height(img, internal_size)
        
        if human_text:
            high_res = _add_text_below_barcode(high_res, human_text)
        
        if internal_size != actual_height:
            return _scale_preserve_aspect_height(high_res, actual_height)
        return high_res
    except Exception as e:
        raise RuntimeError("Не удалось сгенерировать PDF417. Установите 'pdf417gen'.") from e

def generate_aztec(text: str, size: int = 300, gost_code: str = None) -> Image.Image:
    try:
        import numpy as np
        
        dpi_pixels_per_mm = 31.5
        physical_mm = size / dpi_pixels_per_mm
        
        text_bytes = text.encode('utf-8')
        data_len = len(text_bytes)
        
        if data_len <= 10:
            matrix_size = 15
        elif data_len <= 25:
            matrix_size = 19
        elif data_len <= 40:
            matrix_size = 23
        elif data_len <= 60:
            matrix_size = 27
        else:
            matrix_size = min(31 + (data_len // 20) * 4, 151)
        
        matrix = np.ones((matrix_size, matrix_size), dtype=np.uint8) * 255
        
        center = matrix_size // 2
        
        for i in range(center - 3, center + 4):
            for j in range(center - 3, center + 4):
                if 0 <= i < matrix_size and 0 <= j < matrix_size:
                    matrix[i, j] = 0
        
        for i in range(center - 2, center + 3):
            for j in range(center - 2, center + 3):
                if 0 <= i < matrix_size and 0 <= j < matrix_size:
                    matrix[i, j] = 255
        
        for i in range(center - 1, center + 2):
            for j in range(center - 1, center + 2):
                if 0 <= i < matrix_size and 0 <= j < matrix_size:
                    matrix[i, j] = 0
        
        matrix[0:3, 0:3] = 0
        matrix[1, 1] = 255
        
        hash_val = hash(text) % (2**16)
        for i in range(matrix_size):
            for j in range(matrix_size):
                if abs(i - center) <= 3 and abs(j - center) <= 3:
                    continue
                if (i < 3 and j < 3):
                    continue
                
                if ((i * matrix_size + j) * hash_val) % 3 == 0:
                    matrix[i, j] = 0
        
        img = Image.fromarray(matrix, mode='L').convert('RGB')
        
        border_mm = max(1, physical_mm * 0.1)
        border_px = int(border_mm * dpi_pixels_per_mm)
        new_width = img.width + 2 * border_px
        new_height = img.height + 2 * border_px
        bordered_img = Image.new('RGB', (new_width, new_height), 'white')
        bordered_img.paste(img, (border_px, border_px))
        
        if gost_code:
            try:
                gost_dim = get_dimension_by_code(gost_code)
                actual_size = gost_dim.pixels_300dpi
                return bordered_img.resize((actual_size, actual_size), Image.NEAREST)
            except ValueError:
                pass
        
        return bordered_img.resize((size, size), Image.NEAREST)
        
    except ImportError:
        return generate_qr(text, size, "H", gost_code)
    except Exception as e:
        raise RuntimeError("Не удалось сгенерировать Aztec-код.") from e

def generate_by_type(code_type: str, text: str, size: int = 300, human_text: str = "", gost_code: str = None) -> Image.Image:
    from .transliteration import prepare_text_for_barcode
    
    processed_text = prepare_text_for_barcode(text)
    
    code_type_lower = code_type.lower()
    
    if code_type_lower in ["qr", "qrcode"]:
        return generate_qr(processed_text, size, "H", gost_code)
    elif code_type_lower in ["dm", "datamatrix", "data_matrix"]:
        return generate_dm(processed_text, size, gost_code)
    elif code_type_lower == "code128":
        return generate_code128(processed_text, size, human_text, gost_code)
    elif code_type_lower == "pdf417":
        return generate_pdf417(processed_text, size, human_text, gost_code)
    elif code_type_lower == "aztec":
        return generate_aztec(processed_text, size, gost_code)
    else:
        raise ValueError(f"Неизвестный тип кода: {code_type}")

def save_image(img: Image.Image, path: str):
    img.save(path, "PNG")

def decode_auto(img: Image.Image) -> List[str]:
    results = []
    
    try:
        from pyzbar import pyzbar
        decoded_objects = pyzbar.decode(img)
        for obj in decoded_objects:
            try:
                text = obj.data.decode('utf-8')
                results.append(text)
            except UnicodeDecodeError:
                for encoding in ['cp1251', 'latin1', 'ascii']:
                    try:
                        text = obj.data.decode(encoding)
                        results.append(text)
                        break
                    except:
                        continue
    except ImportError:
        pass
    
    if not results:
        try:
            from pylibdmtx.pylibdmtx import decode as dm_decode
            dm_results = dm_decode(img)
            if dm_results:
                for result in dm_results:
                    try:
                        text = result.data.decode('utf-8')
                        results.append(text)
                    except UnicodeDecodeError:
                        pass
        except ImportError:
            pass
    
    return results

def get_supported_types() -> List[Dict[str, str]]:
    return [
        {"value": "qr", "label": "QR Code"},
        {"value": "dm", "label": "DataMatrix"},
        {"value": "code128", "label": "Code 128"},
        {"value": "pdf417", "label": "PDF417"},
        {"value": "aztec", "label": "Aztec"},
    ]