import os
import json


def write_to_disk(data, filename, path):
    """Writes data to a JSON file on disk"""
    os.makedirs(path, exist_ok=True)
    full_path = os.path.join(path, filename)
    
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return full_path

__all__ = [
    "write_to_disk"
]