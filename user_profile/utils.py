import uuid
from PIL import Image
from io import BytesIO


def generate_filename() -> str:
    return str(uuid.uuid4()) + '.webp'


def create_image(image):
    name = generate_filename()
    image = Image.open(image)
    image_file = BytesIO()
    image.save(image_file, format='WEBP')
    image_file.seek(0)
    return name, image_file