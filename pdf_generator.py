import os
import tempfile
from pathlib import Path

try:
    import img2pdf
except ImportError:
    img2pdf = None

from PIL import Image


ALPHA_MODES = {'RGBA', 'RGBa', 'LA', 'La', 'PA', 'P'}


def _ensure_no_alpha(image_path):
    img = Image.open(image_path)
    if img.mode in ALPHA_MODES:
        rgb = img.convert('RGB')
        tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        tmp.close()
        rgb.save(tmp.name, 'JPEG', quality=95)
        return tmp.name, True
    return image_path, False


def _generate_img2pdf(image_paths, output_path, page_size, orientation, progress_callback=None):
    cleaned = []
    temps = []
    total = len(image_paths)
    for i, p in enumerate(image_paths):
        if progress_callback:
            progress_callback(i + 1, total, f"Preprocesando {i + 1} de {total}")
        path, is_temp = _ensure_no_alpha(p)
        cleaned.append(path)
        if is_temp:
            temps.append(path)
    if progress_callback:
        progress_callback(total, total, "Generando PDF...")
    try:
        if page_size == 'Original':
            with open(output_path, 'wb') as f:
                f.write(img2pdf.convert(cleaned))
        else:
            sizes_pt = {
                'A4': (595.28, 841.89),
                'Letter': (612, 792),
                'Legal': (612, 1008),
            }
            w, h = sizes_pt.get(page_size, (595.28, 841.89))
            if orientation == 'Landscape':
                w, h = h, w
            layout = img2pdf.get_layout_fun(pagesize=(w, h))
            with open(output_path, 'wb') as f:
                f.write(img2pdf.convert(cleaned, layout_fun=layout))
    finally:
        for t in temps:
            try:
                os.remove(t)
            except Exception:
                pass


def _generate_pillow(image_paths, output_path, page_size, orientation, quality, progress_callback):
    images = []
    total = len(image_paths)

    for i, path in enumerate(image_paths):
        img = Image.open(path).convert('RGB')

        if page_size != 'Original':
            sizes_pt = {
                'A4': (595.28, 841.89),
                'Letter': (612, 792),
                'Legal': (612, 1008),
            }
            pw, ph = sizes_pt.get(page_size, (595.28, 841.89))
            if orientation == 'Landscape':
                pw, ph = ph, pw

            img_ratio = img.width / img.height
            page_ratio = pw / ph

            if img_ratio > page_ratio:
                new_w = int(pw)
                new_h = int(pw / img_ratio)
            else:
                new_h = int(ph)
                new_w = int(ph * img_ratio)

            img = img.resize((new_w, new_h), Image.LANCZOS)

            new_img = Image.new('RGB', (int(pw), int(ph)), (255, 255, 255))
            x = (int(pw) - img.width) // 2
            y = (int(ph) - img.height) // 2
            new_img.paste(img, (x, y))
            img = new_img

        images.append(img)
        if progress_callback:
            progress_callback(i + 1, total, f"Processing {i + 1} of {total}")

    if images:
        images[0].save(
            output_path,
            save_all=True,
            append_images=images[1:],
            quality=quality
        )


def generate_pdf(image_paths, output_path, page_size='A4', orientation='Portrait', quality=95, progress_callback=None):
    if progress_callback:
        progress_callback(0, 1, "Generating PDF...")

    if img2pdf is not None:
        _generate_img2pdf(image_paths, output_path, page_size, orientation, progress_callback)
    else:
        _generate_pillow(image_paths, output_path, page_size, orientation, quality, progress_callback)

    if progress_callback:
        progress_callback(1, 1, f"PDF saved: {Path(output_path).name}")
