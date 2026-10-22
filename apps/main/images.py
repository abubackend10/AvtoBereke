from io import BytesIO
from pathlib import PurePosixPath

from django.core.files.base import ContentFile, File
from django.db.models.fields.files import ImageFieldFile
from PIL import Image, ImageOps


MAX_IMAGE_SIZE = (1920, 1920)
SUPPORTED_FORMATS = {"JPEG", "PNG", "WEBP"}


def optimize_image_upload(name: str, uploaded_file: File) -> tuple[str, File]:
    with Image.open(uploaded_file) as source:
        image_format = source.format
        if image_format not in SUPPORTED_FORMATS:
            uploaded_file.seek(0)
            return name, uploaded_file

        image = ImageOps.exif_transpose(source)
        was_oversized = image.width > MAX_IMAGE_SIZE[0] or image.height > MAX_IMAGE_SIZE[1]
        image.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
        has_transparency = (
            "A" in image.getbands()
            and image.getchannel("A").getextrema()[0] < 255
        ) or "transparency" in image.info

        output = BytesIO()
        output_name = name
        if image_format == "JPEG" or (image_format == "PNG" and not has_transparency):
            if has_transparency:
                background = Image.new("RGB", image.size, "white")
                background.paste(image, mask=image.getchannel("A"))
                image = background
            else:
                image = image.convert("RGB")
            image.save(output, format="JPEG", quality=82, optimize=True, progressive=True)
            output_name = str(PurePosixPath(output_name).with_suffix(".jpg"))
        elif image_format == "WEBP":
            image.save(output, format="WEBP", quality=82, method=6)
        else:
            image.save(output, format="PNG", optimize=True)

    if output.tell() >= uploaded_file.size and not was_oversized:
        uploaded_file.seek(0)
        return name, uploaded_file

    return output_name, ContentFile(output.getvalue(), name=output_name)


def optimize_image_field(image_field: ImageFieldFile) -> None:
    if not image_field or image_field._committed:
        return

    name, optimized_file = optimize_image_upload(image_field.name, image_field.file)
    if optimized_file is not image_field.file:
        image_field.save(name, optimized_file, save=False)
