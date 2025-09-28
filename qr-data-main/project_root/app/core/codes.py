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

    # Ensure minimum high-quality size
    min_size = max(size, 600)  # Minimum 600px for high quality
    
    # Calculate high DPI box size for crisp printing (300 DPI equivalent)
    target_dpi = 300
    base_box_size = max(8, min_size // 37)  # Adaptive box size based on image size
    
    last_err: Optional[Exception] = None
    for lvl in try_levels:
        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=ecc_map[lvl],
                box_size=base_box_size,
                border=8  # Increased border for better scanning
            )
            qr.add_data(text)
            qr.make(fit=True)
            
            # Get actual matrix size after fitting
            matrix = qr.get_matrix()
            n_modules = len(matrix)
            border = qr.border
            total_modules = n_modules + border * 2
            
            # Calculate optimal box size for target resolution
            box_size = max(base_box_size, min_size // total_modules)
            qr.box_size = box_size
            
            # Generate high-quality image with precise dimensions
            img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
            
            # Calculate actual output dimensions
            actual_size = total_modules * box_size
            
            # Scale to exact target size using high-quality resampling if needed
            if actual_size != size:
                # For upscaling, use LANCZOS for smooth results
                # For downscaling from high-res, use LANCZOS to maintain sharpness
                if actual_size > size:
                    img = img.resize((size, size), Image.LANCZOS)
                else:
                    # For upscaling, use nearest neighbor to maintain sharp edges
                    img = _scale_nearest_exact(img, size)

            # ---- вставляем логотип ----
            logo_path = os.path.join(os.path.dirname(__file__), "..", "static", "star.png")
            logo_path = os.path.abspath(logo_path)
            if os.path.exists(logo_path):
                logo = Image.open(logo_path).convert("RGBA")
                # Smaller logo for high error correction to ensure scannability
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
    
    # Ensure minimum high-quality size for DataMatrix
    min_size = max(size, 600)
    
    en = dm_encode(text.encode("utf-8"))
    base = Image.frombytes('RGB', (en.width, en.height), en.pixels)
    
    # Scale using nearest neighbor to maintain sharp edges for matrix codes
    if base.size[0] < min_size:
        # Calculate scaling factor for high-quality output
        scale_factor = min_size // max(base.size)
        scale_factor = max(scale_factor, 8)  # Minimum 8x scaling for crisp output
        high_res = base.resize(
            (base.size[0] * scale_factor, base.size[1] * scale_factor), 
            Image.NEAREST
        )
        # Then scale down to target size if needed
        if high_res.size[0] != size:
            return high_res.resize((size, size), Image.LANCZOS)
        return high_res
    
    return _scale_nearest_exact(base, size)

def generate_code128(text: str, size: int = 300, human_text: str = "") -> Image.Image:
    """Generate Code 128 barcode using python-barcode.
    Returns image scaled by height to target size, preserving aspect ratio.
    """
    try:
        import barcode  # type: ignore
        from barcode.writer import ImageWriter  # type: ignore
        Code128 = barcode.get_barcode_class('code128')
        code = Code128(text, writer=ImageWriter())
        bio = io.BytesIO()
        
        # Настройки для отображения текста под кодом
        options = {
            "module_height": 15.0, 
            "quiet_zone": 2.0, 
            "font_size": 0,
            "text_distance": 5.0,
            "write_text": bool(human_text)
        }
        
        code.write(bio, options=options)
        bio.seek(0)
        img = Image.open(bio).convert("RGB")
        
        # Если есть текст для отображения, добавляем его
        if human_text:
            img = _add_text_below_barcode(img, human_text)
        
        return _scale_preserve_aspect_height(img, size)
    except Exception as e:
        raise RuntimeError("Не удалось сгенерировать Code128. Установите 'python-barcode'.") from e

def generate_pdf417(text: str, size: int = 300, human_text: str = "") -> Image.Image:
    """Generate PDF417 barcode using pdf417gen."""
    try:
        import pdf417gen  # type: ignore
        codes = pdf417gen.encode(text, columns=6, security_level=2)
        img = pdf417gen.render_image(codes, scale=3, ratio=3)
        img = img.convert("RGB")
        
        # Если есть текст для отображения, добавляем его
        if human_text:
            img = _add_text_below_barcode(img, human_text)
        
        return _scale_preserve_aspect_height(img, size)
    except Exception as e:
        raise RuntimeError("Не удалось сгенерировать PDF417. Установите 'pdf417gen'.") from e

def generate_aztec(text: str, size: int = 300) -> Image.Image:
    """Generate Aztec code using aztec-code-generator library."""
    try:
        from aztec_code_generator import AztecCode
        import numpy as np
        
        # Create an Aztec code
        code = AztecCode(text)
        matrix = code.matrix
        
        # Convert matrix to PIL Image
        # Aztec matrix: True = black module, False = white module
        arr = np.array(matrix, dtype=np.uint8)
        # Convert boolean to 0/255 (False->255=white, True->0=black)
        arr = (arr == False) * 255
        
        # Create PIL image
        img = Image.fromarray(arr, mode='L').convert('RGB')
        
        # Add border (4 modules on each side)
        border = 4
        new_width = img.width + 2 * border
        new_height = img.height + 2 * border
        bordered_img = Image.new('RGB', (new_width, new_height), 'white')
        bordered_img.paste(img, (border, border))
        
        # Scale to requested size
        return _scale_nearest_exact(bordered_img, size)
        
    except ImportError:
        # Fallback to QR code if aztec-code-generator is not available
        # Use high-quality settings for fallback QR code
        import qrcode
        
        min_size = max(size, 600)
        base_box_size = max(8, min_size // 37)
        
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=base_box_size,
            border=8
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        matrix = qr.get_matrix()
        n_modules = len(matrix)
        border = qr.border
        total_modules = n_modules + border * 2
        
        box_size = max(base_box_size, min_size // total_modules)
        qr.box_size = box_size
        
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        actual_size = total_modules * box_size
        
        if actual_size != size:
            if actual_size > size:
                img = img.resize((size, size), Image.LANCZOS)
            else:
                img = _scale_nearest_exact(img, size)
        
        return img
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