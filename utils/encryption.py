from Crypto.Cipher import AES
import base64
import os
import hashlib
import subprocess


# 获取设备唯一 ID
def get_device_id():
    try:
        cpu_id = subprocess.check_output("dmidecode -s processor-version", shell=True).decode().strip()
        board_id = subprocess.check_output("cat /sys/class/dmi/id/product_uuid", shell=True).decode().strip()
        disk_id = subprocess.check_output("lsblk -o SERIAL", shell=True).decode().strip()

        device_string = f"{cpu_id}-{board_id}-{disk_id}"
        device_id = hashlib.sha256(device_string.encode()).hexdigest()
        return device_id[:32]  # 取前32位作为AES密钥
    except Exception as e:
        raise Exception("Failed to retrieve device ID")


# AES-256-GCM 加密
def encrypt_data(data, key):
    cipher = AES.new(key.encode(), AES.MODE_GCM)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data.encode())
    return base64.b64encode(nonce + ciphertext + tag).decode()


# AES-256-GCM 解密
def decrypt_data(enc_data, key):
    raw = base64.b64decode(enc_data.encode())
    nonce, ciphertext, tag = raw[:16], raw[16:-16], raw[-16:]
    cipher = AES.new(key.encode(), AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()
