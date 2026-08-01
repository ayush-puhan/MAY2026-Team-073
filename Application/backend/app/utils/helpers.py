import base64
import os
import uuid
from flask import current_app

def save_base64_image(data_url):
    dir_loc = current_app.config["UNI_BANNER_UPLOAD_DIR"]
    header, encoded = data_url.split(",", 1)

    extension = header.split("/")[1].split(";")[0]

    filename = f"{uuid.uuid4()}.{extension}"
    filepath = os.path.join(dir_loc, filename)

    os.makedirs(dir_loc, exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(encoded))

    return os.path.join("uploads","university_banner",filename)


def delete_uploaded_file(file_url):
    if not file_url:
        return

    # Remove leading '/' if present
    relative_path = file_url.lstrip("/")

    dir_loc = current_app.config["BASE_DIR"]
    file_path = os.path.join(dir_loc, relative_path)
    print(file_path)
    if os.path.isfile(file_path):
        os.remove(file_path)