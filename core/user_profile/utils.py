import uuid
from PIL import Image
from io import BytesIO


def create_image(image):
    _uuid = str(uuid.uuid4())
    name = _uuid + '.webp'
    image = Image.open(image)
    image_file = BytesIO()
    image.save(image_file, format='WEBP')
    image_file.seek(0)
    return name, image_file