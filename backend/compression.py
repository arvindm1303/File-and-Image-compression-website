import os
from PIL import Image
from pypdf import PdfReader, PdfWriter
import zipfile
import io

def compress_image(input_path, output_path, quality):
    img = Image.open(input_path)
    # Convert to RGB if it's a JPEG to avoid issues with RGBA
    if img.format == 'JPEG' or input_path.lower().endswith(('.jpg', '.jpeg')):
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(output_path, "JPEG", quality=quality, optimize=True)
    elif img.format == 'PNG' or input_path.lower().endswith('.png'):
        # For PNG, quality is not directly supported in the same way
        # We can use optimize=True and reduce colors if quality is low
        if quality < 50:
            img = img.convert("P", palette=Image.ADAPTIVE, colors=256)
        img.save(output_path, "PNG", optimize=True)
    else:
        # Default save for other formats
        img.save(output_path, optimize=True)

def compress_pdf(input_path, output_path, quality):
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # pypdf compression
    for page in writer.pages:
        page.compress_content_streams()  # This is CPU intensive but helps

    with open(output_path, "wb") as f:
        writer.write(f)

def compress_docx(input_path, output_path, quality):
    # docx files are already zip files. We can try to re-compress the zip
    # or just open and save it which might apply some default optimization
    # but python-docx doesn't do much.
    # A better way is to re-zip with higher compression level
    
    with zipfile.ZipFile(input_path, 'r') as zin:
        with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zout:
            for item in zin.infolist():
                zout.writestr(item, zin.read(item.filename))

def compress_file(input_path, output_path, quality, file_type):
    if file_type.lower() in ['jpg', 'jpeg', 'png']:
        compress_image(input_path, output_path, quality)
    elif file_type.lower() == 'pdf':
        compress_pdf(input_path, output_path, quality)
    elif file_type.lower() == 'docx':
        compress_docx(input_path, output_path, quality)
    else:
        # Fallback: just copy if unknown type (should not happen with validation)
        import shutil
        shutil.copy(input_path, output_path)
