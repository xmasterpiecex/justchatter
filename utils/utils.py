from fastapi import HTTPException

from PIL import Image

async def create_image(file_data: bytes, client_id: str):
    path = f"./imgs/img{client_id}.jpg"
    try:
        with open(path, "wb") as f:
            f.write(file_data)
        old_image = Image.open(path)
        new_image = old_image.resize((200, 200), Image.Resampling.LANCZOS)
        new_image.save(path, optimize=True, quality=95)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return path
