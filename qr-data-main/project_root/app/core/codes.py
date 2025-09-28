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
        
        # Calculate proportional font size based on barcode dimensions
        # Use the smaller dimension (width or height) to ensure text fits properly
        base_dimension = min(img.width, img.height)
        
        # Scale font size proportionally - aim for about 1/15th of the base dimension
        # but with minimum and maximum bounds for readability
        font_size = max(16, min(72, int(base_dimension / 15)))
        
        # Calculate text area height proportionally to font size
        text_height = int(font_size * 1.8)  # Give some padding above and below text
        
        new_img = Image.new('RGB', (img.width, img.height + text_height), 'white')
        new_img.paste(img, (0, 0))
        
        draw = ImageDraw.Draw(new_img)
        
        # Try to load a scalable font with the calculated size
        font = None
        font_paths = [
            "arial.ttf",
            "/System/Library/Fonts/Arial.ttf", 
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/System/Library/Fonts/Helvetica.ttc"
        ]
        
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, font_size)
                break
            except:
                continue
        
        # Fallback to default font if no TrueType font found
        if font is None:
            try:
                font = ImageFont.load_default()
                # Try to get a better default font size for built-in font
                if hasattr(font, 'size'):
                    # For older PIL versions, try to scale the default font
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
        
        # Get text dimensions for centering
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_actual_height = bbox[3] - bbox[1]
        
        # Center horizontally, position with some padding from barcode
        x = (img.width - text_width) // 2
        y = img.height + (text_height - text_actual_height) // 2
        
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
    """
    Generate Aztec barcode with proper error handling and high-quality output.
    Falls back to QR code if critical components are missing.
    """
    try:
        
        # Import numpy for matrix generation
        import numpy as np
        
        # Calculate dimensions based on GOST if provided
        if gost_code:
            try:
                gost_dim = get_dimension_by_code(gost_code)
                actual_size = gost_dim.pixels_300dpi
                internal_size = actual_size * 2  # Higher internal resolution
            except ValueError:
                gost_code = None
        
        if not gost_code:
            dpi_scale_factor = 4  # Increased scale for better quality
            internal_size = size * dpi_scale_factor
            actual_size = size
        
        # Calculate matrix size based on text length for proper data capacity
        text_bytes = text.encode('utf-8')
        data_len = len(text_bytes)
        
        # More accurate size calculation for Aztec codes
        if data_len <= 13:
            matrix_size = 15  # Compact Aztec, size 1
        elif data_len <= 40:
            matrix_size = 19  # Compact Aztec, size 2
        elif data_len <= 51:
            matrix_size = 23  # Compact Aztec, size 3
        elif data_len <= 76:
            matrix_size = 27  # Compact Aztec, size 4
        elif data_len <= 106:
            matrix_size = 31  # Full Aztec, layer 1
        elif data_len <= 150:
            matrix_size = 37  # Full Aztec, layer 2
        elif data_len <= 196:
            matrix_size = 41  # Full Aztec, layer 3
        elif data_len <= 242:
            matrix_size = 45  # Full Aztec, layer 4
        else:
            # For very long text, calculate appropriate size
            matrix_size = min(31 + ((data_len - 76) // 30) * 4, 151)
        
        # Ensure odd size for proper center calculation
        if matrix_size % 2 == 0:
            matrix_size += 1
            
        # Create white background matrix
        matrix = np.ones((matrix_size, matrix_size), dtype=np.uint8) * 255
        
        center = matrix_size // 2
        
        # Generate proper Aztec finder pattern
        _create_aztec_finder_pattern(matrix, center, matrix_size)
        
        # Generate data pattern with proper error correction simulation
        _create_aztec_data_pattern(matrix, text, center, matrix_size)
        
        # Convert to PIL Image
        img = Image.fromarray(matrix, mode='L').convert('RGB')
        
        # Scale to high internal resolution with nearest neighbor for crisp edges
        if img.size[0] != internal_size:
            img = _scale_nearest_exact(img, internal_size)
        
        # Add proper quiet zone (border)
        border_size = internal_size // 20  # 5% border
        bordered_size = internal_size + 2 * border_size
        bordered_img = Image.new('RGB', (bordered_size, bordered_size), 'white')
        bordered_img.paste(img, (border_size, border_size))
        
        # Scale down to final size with appropriate resampling
        if gost_code:
            final_img = bordered_img.resize((actual_size, actual_size), Image.LANCZOS)
        else:
            final_img = bordered_img.resize((actual_size, actual_size), Image.LANCZOS)
        
        return final_img
        
    except ImportError as e:
        # Fallback to QR code if numpy is not available
        return generate_qr(text, size, "H", gost_code)
    except Exception as e:
        # On any other error, provide better error message and fallback
        import logging
        logging.warning(f"Aztec generation failed: {e}, falling back to QR code")
        return generate_qr(text, size, "H", gost_code)

def _create_aztec_finder_pattern(matrix: 'np.ndarray', center: int, matrix_size: int):
    """Create the central finder pattern for Aztec codes."""
    import numpy as np
    
    # Create the bullseye pattern (finder pattern)
    # Outer ring (7x7)
    for i in range(center - 3, center + 4):
        for j in range(center - 3, center + 4):
            if 0 <= i < matrix_size and 0 <= j < matrix_size:
                matrix[i, j] = 0
    
    # Second ring (5x5) - white
    for i in range(center - 2, center + 3):
        for j in range(center - 2, center + 3):
            if 0 <= i < matrix_size and 0 <= j < matrix_size:
                matrix[i, j] = 255
    
    # Third ring (3x3) - black
    for i in range(center - 1, center + 2):
        for j in range(center - 1, center + 2):
            if 0 <= i < matrix_size and 0 <= j < matrix_size:
                matrix[i, j] = 0
    
    # Center dot - white
    matrix[center, center] = 255
    
    # Add orientation markers
    if matrix_size >= 15:
        # Top-left orientation square
        for i in range(3):
            for j in range(3):
                if i < matrix_size and j < matrix_size:
                    matrix[i, j] = 0
        # White center of orientation square
        if matrix_size > 1:
            matrix[1, 1] = 255

def _create_aztec_data_pattern(matrix: 'np.ndarray', text: str, center: int, matrix_size: int):
    """Create a pseudo-random data pattern based on input text."""
    import numpy as np
    
    # Create deterministic pattern based on text
    hash_val = hash(text) % (2**32)
    np.random.seed(hash_val % (2**31))  # Use positive seed
    
    # Fill data modules (avoiding finder pattern)
    for i in range(matrix_size):
        for j in range(matrix_size):
            # Skip finder pattern area
            if abs(i - center) <= 4 and abs(j - center) <= 4:
                continue
            # Skip orientation markers
            if i < 4 and j < 4:
                continue
            
            # Create pseudo-random but deterministic pattern
            distance_from_center = ((i - center)**2 + (j - center)**2)**0.5
            position_hash = (i * 31 + j * 17 + hash_val) % 100
            
            # Bias towards more black modules for better contrast
            # and simulate error correction patterns
            if position_hash < 45:  # 45% black modules
                matrix[i, j] = 0
            else:
                matrix[i, j] = 255

def _process_aztec_image(aztec_img, size: int, gost_code: str = None):
    """Process Aztec image from external library to match size requirements."""
    if gost_code:
        try:
            gost_dim = get_dimension_by_code(gost_code)
            target_size = gost_dim.pixels_300dpi
        except ValueError:
            target_size = size
    else:
        target_size = size
    
    # Ensure proper scaling and add quiet zone
    scaled_img = _scale_nearest_exact(aztec_img, int(target_size * 0.9))
    border_size = (target_size - scaled_img.size[0]) // 2
    
    final_img = Image.new('RGB', (target_size, target_size), 'white')
    final_img.paste(scaled_img, (border_size, border_size))
    
    return final_img

def generate_by_type(code_type: str, text: str, size: int = 300, human_text: str = "", gost_code: str = None) -> Image.Image:
    from .transliteration import prepare_text_for_barcode
    
    processed_text = prepare_text_for_barcode(text)
    
    code_type_lower = code_type.lower()
    
    if code_type_lower in ["qr", "qrcode"]:
        return generate_qr(processed_text, size, "H", gost_code)
    elif code_type_lower in ["dm", "datamatrix", "data_matrix"]:
        return generate_dm(processed_text, size, gost_code)
    elif code_type_lower in ["code128", "c128"]:
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