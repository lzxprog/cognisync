from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from utils.encryption import encrypt_data, get_device_id
from config import DATA_STORAGE

router = APIRouter()


@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    try:
        # 读取文件内容
        file_bytes = await file.read()

        # 生成设备密钥
        device_key = get_device_id()

        # 加密文件内容
        encrypted_data = encrypt_data(file_bytes.decode("utf-8"), device_key)

        # 确保存储目录存在
        os.makedirs(DATA_STORAGE, exist_ok=True)

        # 生成加密文件路径
        file_path = os.path.join(DATA_STORAGE, f"{file.filename}.enc")

        # 写入加密数据
        with open(file_path, "w") as f:
            f.write(encrypted_data)

        return {"message": "File uploaded and encrypted successfully", "file": file.filename}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")
