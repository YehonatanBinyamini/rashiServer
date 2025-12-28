import os
import time
import io
from PIL import Image


def save_image(file, upload_folder):
    file_bytes = file.read()
    img = Image.open(io.BytesIO(file_bytes))
    ext = img.format.lower()

    file.stream.seek(0)

    timestamp = int(time.time())
    filename = f"{timestamp}.{ext}"
    path = os.path.join(upload_folder, filename)
    file.save(path)

    return {
        "id": str(timestamp),
        "name": filename,
        "mimeType": f"image/{ext}",
        "createdTime": str(timestamp),
    }


def list_images(upload_folder):
    files = []
    for fname in os.listdir(upload_folder):
        if "." not in fname:
            continue
        ts = fname.split(".")[0]
        if not ts.isdigit():
            continue

        files.append({
            "id": ts,
            "name": fname,
            "mimeType": f"image/{fname.split('.')[-1]}",
            "createdTime": ts
        })

    return sorted(files, key=lambda x: int(x["id"]), reverse=True)


def find_image(upload_folder, file_id):
    for fname in os.listdir(upload_folder):
        if fname.startswith(file_id):
            return fname
    return None


def delete_image(upload_folder, file_id):
    deleted = False
    for fname in os.listdir(upload_folder):
        if fname.startswith(file_id):
            os.remove(os.path.join(upload_folder, fname))
            deleted = True
    return deleted
