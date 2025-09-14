from io import BytesIO

from django.core.exceptions import ValidationError

from PIL import Image
from faker import Faker

fake = Faker()


def compress_image(file):
    """
    To compress the size of images uploaded by users.
    """
    image = Image.open(file)

    output = BytesIO()

    width, height = image.size
    
    try:
        resample_filter = Image.Resampling.LANCZOS
    except AttributeError:
        resample_filter = Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS
    image = image.resize(
        (int(width/2), int(height/2)),
        resample_filter,
    )
    image.save(output, optimize=True, quality=95)
    output.seek(0)
    

    return image


def file_size(value):
    """
    limits the size of file that can be uploaded by user
    """
    limit = 5 * 1024 * 1024  # 5 MiB
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 5 MiB')
