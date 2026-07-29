import os
import tempfile
from pathlib import Path
from PIL import Image, ImageOps

try:
    import img2pdf
except ImportError:
    img2pdf = None


def get_unique_filepath(filepath):
    """
    Si el archivo existe (ej: PDF.pdf), genera un nombre único
    añadiendo _1, _2, etc. (ej: PDF_1.pdf) para no reemplazar el existente.
    """
    path = Path(filepath)
    if not path.exists():
        return str(path)

    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    counter = 1

    while True:
        candidate = parent / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return str(candidate)
        counter += 1


def _prepare_image(image_path, quality=95, original_mode="fit_width"):
    """
    Abre la imagen, corrige su orientación EXIF, elimina transparencias,
    y aplica la regla de dimensión según el modo elegido.
    """
    img = Image.open(image_path)

    # 1. Aplicar orientación EXIF nativa si existe
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    # 2. Convertir a RGB (elimina transparencias Alpha/RGBA)
    rgb = img.convert('RGB')

    # 3. Si el modo es max_1920, limitar la dimensión máxima a 1920px
    if original_mode == "max_1920":
        w, h = rgb.size
        if w > 1920 or h > 1920:
            rgb.thumbnail((1920, 1920), Image.LANCZOS)

    # 4. Guardar en JPEG temporal con 96 DPI uniforme
    tmp = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
    tmp_path = tmp.name
    tmp.close()

    rgb.save(tmp_path, 'JPEG', quality=quality, dpi=(96, 96))
    return tmp_path


def _generate_img2pdf(prepared_paths, output_path, page_size, orientation, original_mode="fit_width"):
    if page_size == 'Original':
        if original_mode == "fit_width":
            # Píxeles 100% nativos intactos, marco de página ajustado a 600pt para lectura pareja
            def fit_width_layout(w, h, dpi):
                pt_w = 600.0
                pt_h = pt_w * (h / w)
                return (pt_w, pt_h, pt_w, pt_h)

            with open(output_path, 'wb') as f:
                f.write(img2pdf.convert(prepared_paths, layout_fun=fit_width_layout))
        else:
            with open(output_path, 'wb') as f:
                f.write(img2pdf.convert(prepared_paths))
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
            f.write(img2pdf.convert(prepared_paths, layout_fun=layout))


def _generate_pillow(prepared_paths, output_path, page_size, orientation, quality):
    images = []
    for path in prepared_paths:
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

    if images:
        images[0].save(
            output_path,
            save_all=True,
            append_images=images[1:],
            quality=quality
        )


def generate_pdf(image_paths, output_path, page_size='A4', orientation='Portrait', quality=95, original_mode="fit_width", progress_callback=None):
    # Garantizar nombre único sin reemplazar si ya existe (ej: PDF_1.pdf)
    final_output_path = get_unique_filepath(output_path)

    if progress_callback:
        progress_callback(0, len(image_paths), "Preprocesando imágenes...")

    prepared_paths = []
    total = len(image_paths)

    try:
        for i, path in enumerate(image_paths):
            if progress_callback:
                progress_callback(i + 1, total, f"Procesando imagen {i + 1} de {total}")
            prep = _prepare_image(path, quality=quality, original_mode=original_mode)
            prepared_paths.append(prep)

        if progress_callback:
            progress_callback(total, total, "Construyendo documento PDF...")

        success = False
        if img2pdf is not None:
            try:
                _generate_img2pdf(prepared_paths, final_output_path, page_size, orientation, original_mode=original_mode)
                success = True
            except Exception as e:
                print(f"img2pdf falló ({e}), usando motor Pillow...")
                success = False

        if not success:
            _generate_pillow(prepared_paths, final_output_path, page_size, orientation, quality)

    finally:
        for p in prepared_paths:
            try:
                os.remove(p)
            except Exception:
                pass

    if progress_callback:
        progress_callback(total, total, f"PDF guardado: {Path(final_output_path).name}")

    return final_output_path
