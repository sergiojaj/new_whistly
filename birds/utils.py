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
    
    image = image.resize(
                            (int(width/2),
                                int(height/2)
                            ),
                            Image.ANTIALIAS
                        )
    image.save(output, optimize=True, quality=95)
    output.seek(0)
    

    return image


def file_size(value):
    """
    limits the size of file that can be uploaded by user
    """
    limit = 5242880 # 5 megabytes
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 2 MiB')