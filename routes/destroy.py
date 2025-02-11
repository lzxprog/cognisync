from fastapi import APIRouter, HTTPException
import os
import shutil
from utils.secure_delete import secure_wipe
from config import DATA_STORAGE

router = APIRouter()


@router.delete("/{file_id}")
async def destroy_file(file_id: str):
    try:
        file_path = os.path.join(DATA_STORAGE, f"{file_id}.enc")

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")

        # 进行安全擦除
        secure_wipe(file_path)

        return {"message": "File securely destroyed", "file": file_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File destruction failed: {str(e)}")
