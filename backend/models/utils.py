import numpy as np
from PIL import Image
import io
import base64
import uuid
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def image_bytes_to_np(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    return np.array(img)

def data_url_to_bytes(data_url):
    # data:image/png;base64,....
    header, encoded = data_url.split(',', 1)
    return base64.b64decode(encoded)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    return f"{uuid.uuid4().hex}.{ext}"