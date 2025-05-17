from fastapi import UploadFile, HTTPException
import os
import shutil

def save_avatar_file(avatar: UploadFile, name: str, last_name: str, code: str) -> str:
    if not avatar.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo no es una imagen válida")

    file_extension = avatar.filename.split(".")[-1]
    filename = f"{name}_{last_name}_{code}.{file_extension}".replace(" ", "_")
    relative_path = os.path.join("static", "avatars", filename)
    absolute_path = os.path.join("services", "security", relative_path)

    if os.path.exists(absolute_path):
        os.remove(absolute_path)

    with open(absolute_path, "wb") as buffer:
        shutil.copyfileobj(avatar.file, buffer)

    return relative_path
