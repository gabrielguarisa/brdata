import requests
import os, time
import base64
import json
from tqdm import tqdm
from typing import Literal

DEFAULT_PATH = "data/landing/b3"
DEFAULT_INDEX = ["IBOV", "IBBR", "IBBC", "IBBE", "IBEP",
                "IBEW", "IBEE", "IBSD", "IBHB", "IBLV",
                "IDIV", "IBXX", "IBXL", "IBRA", "AGFS",
                "IFNC", "BDRX", "ICON", "IEEX", "IFIX",
                "IFIL", "IMAT", "INDX", "IMOB", "MLCX",
                "SMLL", "UTIL", "IVBX"]

def params_to_base64(params):
    """Converts search parameters to base64"""
    original_bytes = params.encode("utf-8")
    enconded_bytes_base64 = base64.b64encode(original_bytes)
    string_base64 = enconded_bytes_base64.decode("ascii")
    return string_base64

def download_index(index: Literal["IBOV", "IBBR", "IBBC", "IBBE", "IBEP",
                "IBEW", "IBEE", "IBSD", "IBHB", "IBLV",
                "IDIV", "IBXX", "IBXL", "IBRA", "AGFS",
                "IFNC", "BDRX", "ICON", "IEEX", "IFIX",
                "IFIL", "IMAT", "INDX", "IMOB", "MLCX",
                "SMLL", "UTIL", "IVBX"], 
                path: str = DEFAULT_PATH,
                overwrite: bool = False):
    """Extracts JSON files from B3 indexes"""
    os.makedirs(path, exist_ok=True)
        
    every_data = []
    current_page = 1
    index_date = None
    full_path = None
    file = None
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

    while True:
        base = {"language":"pt-br","pageNumber":current_page,"pageSize":100,"index":f"{index}","segment":"1"}
        base_json = json.dumps(base)
        string_base64 = params_to_base64(base_json)
        link = f"https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/{string_base64}"
            
        try:
            response = requests.get(link, headers=headers)
            response.raise_for_status()
            data = response.json()

            if index_date is None:
                index_date = data["header"]["date"].replace("/","-")
                file = f"{index}_{index_date}.json"
                full_path = os.path.join(path, file)
                
                if not overwrite and os.path.exists(full_path):
                    return file
            
            results = data.get('results', [])
            if not results:
                break

            every_data.extend(results)

            total_pages = data.get("page", {}).get("totalPages", 0)
            if current_page >= total_pages:
                break

            current_page += 1
            time.sleep(0.5)
        
        except Exception as e:
            raise Exception(f"Index Error {index}: {e}") from None

    if not index_date or not every_data:
        raise Exception(f"Data Not Found for {index}")
        
    with open(full_path, "w", encoding="utf-8") as arquivo:
        json.dump(every_data, arquivo, indent=4, ensure_ascii=False)
        
    return file
            
def download_indexes(index_list: list[str],   
                     path: str = DEFAULT_PATH,
                     overwrite: bool = False):
    """Extracts JSON files from a list of B3 indices"""
    for i in tqdm(index_list, desc="Download B3"):
        if i not in DEFAULT_INDEX:
            tqdm.write(f"Index {i} Not Found")
            continue
        try:
            download_index(index=i, path=path, overwrite=overwrite)
        except Exception as e:
            tqdm.write(str(e))
