import os
import random
import shutil


def secure_wipe(file_path, passes=5):
    """Securely overwrite and delete a file to prevent recovery."""
    if not os.path.exists(file_path):
        return False

    try:
        size = os.path.getsize(file_path)
        with open(file_path, "wb") as f:
            for _ in range(passes):
                f.write(os.urandom(size))  # Overwrite with random data
                f.flush()
        os.remove(file_path)
        return True
    except Exception as e:
        print(f"Error securely wiping file: {e}")
        return False


def secure_delete_directory(directory):
    """Securely delete an entire directory by wiping all files and removing it."""
    if not os.path.exists(directory):
        return False

    try:
        for root, dirs, files in os.walk(directory, topdown=False):
            for file in files:
                secure_wipe(os.path.join(root, file))
            for dir in dirs:
                shutil.rmtree(os.path.join(root, dir))
        shutil.rmtree(directory)
        return True
    except Exception as e:
        print(f"Error securely deleting directory: {e}")
        return False
