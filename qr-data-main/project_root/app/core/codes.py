from typing import Optional, List, Dict
from PIL import Image
import io
import os

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
    """Добавляет текст под штрих-код"""
    try:
        from PIL import ImageDraw, ImageFont
        
        # Создаем новое изображение с дополнительным местом для текста
        text_height = 30
        new_img = Image.new('RGB', (img.width, img.height + text_height), 'white')
        new_img.paste(img, (0, 0))
        
        # Рисуем текст
        draw = ImageDraw.Draw(new_img)
        
        # Пытаемся использовать системный шрифт
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
            except:
                font = ImageFont.load_default()
        
        # Центрируем текст
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (img.width - text_width) // 2
        y = img.height + 5
        
        draw.text((x, y), text, fill='black', font=font)
        
        return new_img
    except Exception:
        # Если не удалось добавить текст, возвращаем оригинальное изображение
        return img

def generate_qr(text: str, size: int = 300, preferred_ecc: str = "H") -> Image.Image:
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

    # High-DPI scaling factor for print-quality output
    # Generate at 3x resolution internally for crisp 300 DPI equivalent
    dpi_scale_factor = 3
    internal_size = size * dpi_scale_factor
    
    # Ensure minimum high-quality internal size
    min_internal_size = max(internal_size, 1800)  # Minimum 1800px internal for ultra-sharp output
    
    # Calculate high DPI box size for crisp printing
    base_box_size = max(12, min_internal_size // 37)  # Larger box size for high-DPI generation
    
    last_err: Optional[Exception] = None
    for lvl in try_levels:
        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=ecc_map[lvl],
                box_size=base_box_size,
                border=12  # Increased border for better scanning at high resolution
            )
            qr.add_data(text)
            qr.make(fit=True)
            
            # Get actual matrix size after fitting
            matrix = qr.get_matrix()
            n_modules = len(matrix)
            border = qr.border
            total_modules = n_modules + border * 2
            
            # Calculate optimal box size for target internal resolution
            box_size = max(base_box_size, min_internal_size // total_modules)
            qr.box_size = box_size
            
            # Generate high-resolution image internally
            img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
            
            # Calculate actual output dimensions at high resolution
            actual_internal_size = total_modules * box_size
            
            # Scale to exact internal target size if needed using high-quality resampling
            if actual_internal_size != internal_size:
                if actual_internal_size > internal_size:
                    img = img.resize((internal_size, internal_size), Image.LANCZOS)
                else:
                    # For upscaling, use nearest neighbor to maintain sharp edges
                    img = _scale_nearest_exact(img, internal_size)
            
            # Finally scale down to display size using high-quality LANCZOS resampling
            # This maintains crisp edges while reducing size for display
            if internal_size != size:
                img = img.resize((size, size), Image.LANCZOS)

            # ---- вставляем логотип ----
            logo_path = os.path.join(os.path.dirname(__file__), "..", "static", "star.png")
            logo_path = os.path.abspath(logo_path)
            if os.path.exists(logo_path):
                logo = Image.open(logo_path).convert("RGBA")
                # Logo size based on final display size, not internal resolution
                logo_size = size // 8 if lvl == "H" else size // 6
                logo = logo.resize((logo_size, logo_size), Image.LANCZOS)
                pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
                img.paste(logo, pos, mask=logo)

            return img
        except Exception as e:
            last_err = e
            continue
    raise ValueError("Слишком длинный текст для QR даже на уровне L") from last_err
def generate_dm(text: str, size: int = 300) -> Image.Image:
    from pylibdmtx.pylibdmtx import encode as dm_encode
    
    # High-DPI scaling for print-quality DataMatrix
    dpi_scale_factor = 4  # Even higher for DataMatrix due to dense matrix
    internal_size = size * dpi_scale_factor
    min_internal_size = max(internal_size, 2000)  # Higher minimum for DataMatrix precision
    
    en = dm_encode(text.encode("utf-8"))
    base = Image.frombytes('RGB', (en.width, en.height), en.pixels)
    
    # Scale using nearest neighbor to maintain sharp edges for matrix codes
    if base.size[0] < min_internal_size:
        # Calculate scaling factor for ultra-high-quality output
        scale_factor = min_internal_size // max(base.size)
        scale_factor = max(scale_factor, 16)  # Higher minimum scaling for DataMatrix
        high_res = base.resize(
            (base.size[0] * scale_factor, base.size[1] * scale_factor), 
            Image.NEAREST
        )
        # Scale to exact internal size maintaining aspect ratio
        if high_res.size[0] != internal_size:
            high_res = _scale_nearest_exact(high_res, internal_size)
        
        # Finally scale down to display size using LANCZOS for smooth result
        if internal_size != size:
            return high_res.resize((size, size), Image.LANCZOS)
        return high_res
    
    # Direct scaling if already large enough
    scaled = _scale_nearest_exact(base, internal_size)
    if internal_size != size:
        return scaled.resize((size, size), Image.LANCZOS)
    return scaled

def generate_code128(text: str, size: int = 300, human_text: str = "") -> Image.Image:
    """Generate Code 128 barcode using python-barcode.
    Returns image scaled by height to target size, preserving aspect ratio.
    """
    try:
        import barcode  # type: ignore
        from barcode.writer import ImageWriter  # type: ignore
        Code128 = barcode.get_barcode_class('code128')
        
        # High-DPI scaling for barcode generation
        dpi_scale_factor = 3
        internal_size = size * dpi_scale_factor
        
        code = Code128(text, writer=ImageWriter())
        bio = io.BytesIO()
        
        # High-resolution options for crisp barcode output
        options = {
            "module_height": 45.0,  # 3x higher for internal resolution
            "module_width": 0.8,    # Thicker bars for better print quality
            "quiet_zone": 6.0,      # Larger quiet zone
            "font_size": 0,         # Disable built-in text
            "text_distance": 15.0,
            "write_text": False,
            "dpi": 300              # Set DPI for high quality
        }
        
        code.write(bio, options=options)
        bio.seek(0)
        img = Image.open(bio).convert("RGB")
        
        # Scale to internal resolution maintaining aspect ratio
        high_res = _scale_preserve_aspect_height(img, internal_size)
        
        # Add human text at high resolution if specified
        if human_text:
            high_res = _add_text_below_barcode(high_res, human_text)
        
        # Scale down to display size using high-quality resampling
        if internal_size != size:
            return _scale_preserve_aspect_height(high_res, size)
        return high_res
    except Exception as e:
        raise RuntimeError("Не удалось сгенерировать Code128. Установите 'python-barcode'.") from e

def generate_pdf417(text: str, size: int = 300, human_text: str = "") -> Image.Image:
    """Generate PDF417 barcode using pdf417gen."""
    try:
        import pdf417gen  # type: ignore
        
        # High-DPI scaling for PDF417
        dpi_scale_factor = 3
        internal_size = size * dpi_scale_factor
        
        # Generate at higher scale and ratio for print quality
        codes = pdf417gen.encode(text, columns=6, security_level=2)
        img = pdf417gen.render_image(codes, scale=9, ratio=9)  # 3x higher scale
        img = img.convert("RGB")
        
        # Scale to internal resolution maintaining aspect ratio
        high_res = _scale_preserve_aspect_height(img, internal_size)
        
        # Add human text at high resolution if specified
        if human_text:
            high_res = _add_text_below_barcode(high_res, human_text)
        
        # Scale down to display size using high-quality resampling
        if internal_size != size:
            return _scale_preserve_aspect_height(high_res, size)
        return high_res
    except Exception as e:
        raise RuntimeError("Не удалось сгенерировать PDF417. Установите 'pdf417gen'.") from e

def generate_aztec(text: str, size: int = 300) -> Image.Image:
    """Generate Aztec code using aztec-code-generator library."""
    try:
        from aztec_code_generator import AztecCode
        import numpy as np
        
        # High-DPI scaling for print-quality Aztec
        dpi_scale_factor = 3
        internal_size = size * dpi_scale_factor
        min_internal_size = max(internal_size, 1800)
        
        # Create an Aztec code
        code = AztecCode(text)
        matrix = code.matrix
        
        # Convert matrix to PIL Image
        # Aztec matrix: True = black module, False = white module
        arr = np.array(matrix, dtype=np.uint8)
        # Convert boolean to 0/255 (False->255=white, True->0=black)
        arr = (arr == False) * 255
        
        # Create PIL image at base resolution
        img = Image.fromarray(arr, mode='L').convert('RGB')
        
        # Add border (scaled appropriately for high-DPI)
        border_modules = 8  # Larger border for high-DPI
        module_size = max(16, min_internal_size // (len(matrix) + border_modules * 2))
        
        # Scale up using nearest neighbor for crisp matrix
        high_res = img.resize(
            (img.width * module_size, img.height * module_size), 
            Image.NEAREST
        )
        
        # Add border to high-res image
        border_pixels = border_modules * module_size
        bordered_width = high_res.width + 2 * border_pixels
        bordered_height = high_res.height + 2 * border_pixels
        bordered_img = Image.new('RGB', (bordered_width, bordered_height), 'white')
        bordered_img.paste(high_res, (border_pixels, border_pixels))
        
        # Scale to internal target size
        if bordered_img.size[0] != internal_size:
            bordered_img = _scale_nearest_exact(bordered_img, internal_size)
        
        # Finally scale down to display size using LANCZOS
        if internal_size != size:
            return bordered_img.resize((size, size), Image.LANCZOS)
        return bordered_img
        
    except ImportError:
        # Fallback to high-quality QR code
        return generate_qr(text, size, "H")
    except Exception as e:
        raise RuntimeError("Не удалось сгенерировать Aztec-код.") from e

def generate_by_type(code_type: str, text: str, size: int = 300, human_text: str = "") -> Image.Image:
    from .transliteration import prepare_text_for_barcode
    
    # Подготавливаем текст для кодирования (транслитерация кириллицы)
    processed_text = prepare_text_for_barcode(text)
    
    t = (code_type or "QR").upper()
    if t in ("QR",):
        return generate_qr(processed_text, size=size)
    if t in ("DM", "DATAMATRIX", "DATA_MATRIX"):
        return generate_dm(processed_text, size=size)
    if t in ("C128", "CODE128", "CODE_128"):
        return generate_code128(processed_text, size=size, human_text=human_text)
    if t in ("PDF417",):
        return generate_pdf417(processed_text, size=size, human_text=human_text)
    if t in ("AZTEC", "AZTECCODE"):
        return generate_aztec(processed_text, size=size)
    # default to QR
    return generate_qr(processed_text, size=size)

def save_image(img: Image.Image, full_path: str) -> None:
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    # Save with high quality settings for better print results
    # Set DPI metadata to 300 for print quality indication
    img.save(full_path, "PNG", optimize=False, compress_level=1, dpi=(300, 300))

def decode_qr(pil_img: Image.Image) -> Optional[str]:
    import numpy as np
    import cv2
    img = pil_img.convert("RGB")
    arr = np.array(img)
    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(arr)
    if data:
        return data.strip()
    return None

def decode_dm(pil_img: Image.Image) -> Optional[str]:
    from pylibdmtx.pylibdmtx import decode as dm_decode
    res = dm_decode(pil_img)
    if res:
        try:
            return res[0].data.decode("utf-8").strip()
        except Exception:
            return res[0].data.decode("latin-1", errors="replace").strip()
    return None

def decode_with_zbar(pil_img: Image.Image) -> List[Dict]:
    """Try pyzbar to detect additional formats like CODE128 and QR. Returns list of dicts."""
    try:
        from pyzbar.pyzbar import decode as zbar_decode  # type: ignore
        results = zbar_decode(pil_img)
        out: List[Dict] = []
        for r in results:
            typ = (r.type or "").upper()
            data = (r.data or b"").decode("utf-8", errors="replace").strip()
            if not data:
                continue
            if typ == "QRCODE":
                out.append({"type": "QR", "text": data})
            elif typ == "CODE128":
                out.append({"type": "C128", "text": data})
            # zbar typically doesn't support PDF417/AZTEC; ignore others here
        return out
    except Exception:
        return []

def decode_pdf417(pil_img: Image.Image) -> Optional[str]:
    try:
        import pdf417decoder  # type: ignore
        # pdf417decoder expects a path or numpy array; use numpy array
        import numpy as np
        arr = np.array(pil_img.convert("L"))
        decoder = pdf417decoder.PDF417Decoder(arr)
        barcodes = decoder.decode()
        if barcodes:
            # concatenate values if multiple
            text_parts = []
            for bc in barcodes:
                try:
                    text_parts.append(str(bc.value))
                except Exception:
                    pass
            text = "\n".join([t for t in text_parts if t]).strip()
            return text or None
        return None
    except Exception:
        return None

def decode_aztec(pil_img: Image.Image) -> Optional[str]:
    """Decode Aztec code using aztec-code-generator library if available; otherwise try pyzxing."""
    # First try aztec-code-generator library
    try:
        from aztec_code_generator import AztecCode
        import numpy as np
        
        # Convert PIL image to matrix for Aztec decoder
        img_gray = pil_img.convert('L')
        img_arr = np.array(img_gray)
        
        # Convert grayscale to boolean matrix (threshold at 128)
        # True = black module, False = white module
        threshold = 128
        binary_matrix = img_arr < threshold
        
        # Try to decode the Aztec code
        # Note: aztec-code-generator library may not have decoding functionality
        # This is a placeholder for potential future decoding support
        
        # For now, return None as aztec-code-generator doesn't support decoding
        pass
        
    except ImportError:
        pass
    except Exception:
        pass
    
    # Fallback to pyzxing if available
    try:
        from pyzxing import BarCodeReader  # type: ignore
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".png", delete=True) as tmp:
            pil_img.save(tmp.name, format="PNG")
            reader = BarCodeReader()
            res = reader.decode(tmp.name)
            # res can be a list of dicts
            if isinstance(res, list) and res:
                for item in res:
                    fmt = (item.get('format') or "").upper()
                    text = (item.get('raw') or item.get('parsed') or "").strip()
                    if fmt == "AZTEC" and text:
                        return text
        return None
    except Exception:
        return None

def decode_auto(pil_img: Image.Image) -> List[Dict]:
    from .transliteration import process_scanned_text
    
    out: List[Dict] = []
    dm = decode_dm(pil_img)
    if dm:
        processed_text = process_scanned_text(dm)
        out.append({"type": "DM", "text": processed_text})
        return out
    qr = decode_qr(pil_img)
    if qr:
        processed_text = process_scanned_text(qr)
        out.append({"type": "QR", "text": processed_text})
        return out
    # Try additional decoders
    pdf = decode_pdf417(pil_img)
    if pdf:
        processed_text = process_scanned_text(pdf)
        out.append({"type": "PDF417", "text": processed_text})
        return out
    zb = decode_with_zbar(pil_img)
    if zb:
        # prefer the first recognizable type
        result = zb[0].copy()
        result["text"] = process_scanned_text(result["text"])
        out.append(result)
        return out
    az = decode_aztec(pil_img)
    if az:
        processed_text = process_scanned_text(az)
        out.append({"type": "AZTEC", "text": processed_text})
        return out
    for angle in (90, 180, 270):
        rotated = pil_img.rotate(angle, expand=True)
        dm = decode_dm(rotated)
        if dm:
            processed_text = process_scanned_text(dm)
            out.append({"type": "DM", "text": processed_text})
            break
        qr = decode_qr(rotated)
        if qr:
            processed_text = process_scanned_text(qr)
            out.append({"type": "QR", "text": processed_text})
            break
        # Try secondary decoders on rotated image
        if not out:
            pdf = decode_pdf417(rotated)
            if pdf:
                processed_text = process_scanned_text(pdf)
                out.append({"type": "PDF417", "text": processed_text})
                break
        if not out:
            zb = decode_with_zbar(rotated)
            if zb:
                result = zb[0].copy()
                result["text"] = process_scanned_text(result["text"])
                out.append(result)
                break
        if not out:
            az = decode_aztec(rotated)
            if az:
                processed_text = process_scanned_text(az)
                out.append({"type": "AZTEC", "text": processed_text})
                break
    return out