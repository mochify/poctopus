import requests
from PIL import Image
from StringIO import StringIO
from uuid import uuid4

THUMBNAIL_SIZE = 128, 128

def process_image(file_path, name=None):
    if not name:
        name = uuid4()
    img = Image.open(file_path)
    thumbnail = img.copy().thumbnail(THUMBNAIL_SIZE)
    # Output everything to StringIO objects
    orig_sio = StringIO()
    img.save(orig_sio, format='JPEG')
    thumb_sio = StringIO()
    thumbnail.save(thumb_sio, format='JPEG')
    return {
        'name': name,
        'thumbnail': thumb_sio,
        'original': orig_sio
    }


def process_external_file(url, name=None):
    if not name:
        name = uuid4()
    response = requests.get(url)
    if response.status_code == 200:
        img = Image.open(StringIO(response.content))
        thumbnail = img.copy()
        thumbnail.thumbnail(THUMBNAIL_SIZE)
        orig_sio = StringIO()
        thumb_sio = StringIO()
        img.save(orig_sio, format='JPEG')
        thumbnail.save(thumb_sio, format='JPEG')
        # Process the image, generate thumbnails and a processed
        # file, then return them
        # read response.content
        return {
            'name': name,
            'thumbnail': thumb_sio,
            'original': orig_sio
        }
    else:
        return None
