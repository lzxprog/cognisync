from Crypto.Cipher import AES
import base64
import platform
import hashlib
import subprocess

# 获取设备唯一 ID
def get_device_id():
    """根据操作系统获取唯一设备 ID，兼容 Windows 和 Linux/macOS"""
    try:
        if platform.system() == "Windows":
            cpu_id = subprocess.check_output("wmic cpu get ProcessorId", shell=True).decode().split("\n")[1].strip()
            board_id = subprocess.check_output("wmic baseboard get SerialNumber", shell=True).decode().split("\n")[
                1].strip()
            disk_id = subprocess.check_output("wmic diskdrive get SerialNumber", shell=True).decode().split("\n")[
                1].strip()
        else:  # Linux/macOS
            cpu_id = subprocess.check_output("cat /proc/cpuinfo | grep 'model name' | head -1",
                                             shell=True).decode().strip()
            board_id = subprocess.check_output("cat /sys/class/dmi/id/product_uuid", shell=True).decode().strip()
            disk_id = subprocess.check_output("lsblk -o SERIAL | tail -n +2 | head -1", shell=True).decode().strip()

        # 确保所有 ID 变量为字符串类型
        cpu_id = str(cpu_id)
        board_id = str(board_id)
        disk_id = str(disk_id)

        # 生成设备唯一 ID
        device_string = f"{cpu_id}-{board_id}-{disk_id}"
        device_id = hashlib.sha256(device_string.encode()).hexdigest()
        return device_id[:32]  # 取前 32 位作为 AES 密钥
    except Exception as e:
        raise Exception(f"Failed to retrieve device ID: {str(e)}")


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
