import os
import re
import zipfile
import tempfile
from pathlib import Path

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.tif', '.webp'}
ARCHIVE_EXTENSIONS = {'.zip', '.rar'}


def _natural_key(text):
    return [int(part) if part.isdigit() else part.lower()
            for part in re.split(r'(\d+)', text)]


def is_image(filepath):
    return Path(filepath).suffix.lower() in SUPPORTED_EXTENSIONS


def is_archive(filepath):
    return Path(filepath).suffix.lower() in ARCHIVE_EXTENSIONS


def scan_directory(directory):
    results = {'images': [], 'archives': []}
    directory = Path(directory)
    if not directory.exists():
        return results
    for root, dirs, files in os.walk(directory):
        for f in sorted(files, key=_natural_key):
            fpath = os.path.join(root, f)
            if is_image(fpath):
                results['images'].append(fpath)
            elif is_archive(fpath):
                results['archives'].append(fpath)
    return results


def extract_archive(archive_path, extract_dir):
    extracted = []
    archive_path = Path(archive_path)
    ext = archive_path.suffix.lower()

    if ext == '.zip':
        with zipfile.ZipFile(str(archive_path), 'r') as zf:
            zf.extractall(extract_dir)
    elif ext == '.rar':
        import rarfile
        with rarfile.RarFile(str(archive_path), 'r') as rf:
            rf.extractall(extract_dir)

    for root, dirs, files in os.walk(extract_dir):
        for f in sorted(files, key=_natural_key):
            if is_image(f):
                extracted.append(os.path.join(root, f))

    extracted.sort(key=lambda x: _natural_key(Path(x).name))
    return extracted


def collect_from_sources(sources, progress_callback=None):
    image_entries = []
    temp_dirs = []
    total = len(sources)

    for i, source in enumerate(sources):
        if progress_callback:
            progress_callback(i, total, f"Processing: {Path(source).name}")

        if os.path.isdir(source):
            group = Path(source).name
            results = scan_directory(source)
            for img in results['images']:
                image_entries.append((group, img))
            for archive in results['archives']:
                temp_dir = tempfile.mkdtemp(prefix='img2pdf_')
                temp_dirs.append(temp_dir)
                try:
                    extracted = extract_archive(archive, temp_dir)
                    archive_group = Path(archive).stem
                    for img in extracted:
                        image_entries.append((archive_group, img))
                except ImportError:
                    print(f"Cannot extract {Path(archive).name}: rarfile not installed")
                except Exception as e:
                    print(f"Cannot extract {Path(archive).name}: {e}")

        elif is_archive(source):
            group = Path(source).stem
            temp_dir = tempfile.mkdtemp(prefix='img2pdf_')
            temp_dirs.append(temp_dir)
            try:
                extracted = extract_archive(source, temp_dir)
                for img in extracted:
                    image_entries.append((group, img))
            except ImportError:
                print(f"Cannot extract {Path(source).name}: rarfile not installed")
            except Exception as e:
                print(f"Cannot extract {Path(source).name}: {e}")

        elif is_image(source):
            image_entries.append((Path(source).parent.name or "root", source))

    image_entries.sort(key=lambda x: (_natural_key(x[0]), _natural_key(Path(x[1]).name)))
    all_images = [img for _, img in image_entries]

    if progress_callback:
        progress_callback(total, total, f"Found {len(all_images)} images")

    return all_images, temp_dirs
