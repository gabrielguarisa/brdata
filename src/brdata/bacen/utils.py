import os
import json
from datetime import datetime

def write_to_disk(data, filename, path):
    """Writes data to a JSON file on disk"""
    os.makedirs(path, exist_ok=True)
    full_path = os.path.join(path, filename)
    
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return full_path

def date_validator(date: str):
    if date is None:
        return None
    
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return date
    except ValueError:
        raise ValueError(
            f"Invalid date format: '{date}'. Use the format 'YYYY-MM-DD' (example: '2024-01-01')."
        )

__all__ = [
    "write_to_disk",
    "date_validator"
]