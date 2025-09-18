import os
import uuid

from django.conf import settings
from django.utils.text import get_valid_filename


def generate_image_path(image_file):
    folder = os.path.join("uploads", str(uuid.uuid4()))
    os.makedirs(os.path.join(settings.MEDIA_ROOT, folder), exist_ok=True)

    file_name = get_valid_filename(image_file.name)
    print(file_name)
    full_path = os.path.join(folder, file_name)
    print(full_path)
    return full_path
