import requests
import os
import time
import base64
import json
from tqdm import tqdm
from enum import StrEnum


class B3Index(StrEnum):
    IBOV = "IBOV"
    IBBR = "IBBR"
    IBBC = "IBBC"
    IBBE = "IBBE"
    IBEP = "IBEP"
    IBEW = "IBEW"
    IBEE = "IBEE"
    IBSD = "IBSD"
    IBHB = "IBHB"
    IBLV = "IBLV"
    IDIV = "IDIV"
    IBXX = "IBXX"
    IBXL = "IBXL"
    IBRA = "IBRA"
    AGFS = "AGFS"
    IFNC = "IFNC"
    BDRX = "BDRX"
    ICON = "ICON"
    IEEX = "IEEX"
    IFIX = "IFIX"
    IFIL = "IFIL"
    IMAT = "IMAT"
    INDX = "INDX"
    IMOB = "IMOB"
    MLCX = "MLCX"
    SMLL = "SMLL"
    UTIL = "UTIL"
    IVBX = "IVBX"


VALID_INDEXES = {index.value for index in B3Index}


def params_to_base64(params):
    """Converts search parameters to base64"""
    original_bytes = params.encode("utf-8")
    enconded_bytes_base64 = base64.b64encode(original_bytes)
    string_base64 = enconded_bytes_base64.decode("ascii")
    return string_base64


def download_index(
    index: B3Index | str, path: str | None = None, overwrite: bool = False
):
    """Extracts JSON files from B3 indexes"""
    if path:
        os.makedirs(path, exist_ok=True)

    every_data = []
    current_page = 1
    header = None
    full_path = None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    while True:
        base = {
            "language": "pt-br",
            "pageNumber": current_page,
            "pageSize": 100,
            "index": f"{index}",
            "segment": "1",
        }
        base_json = json.dumps(base)
        string_base64 = params_to_base64(base_json)
        link = f"https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/{string_base64}"

        try:
            response = requests.get(link, headers=headers)
            response.raise_for_status()
            data = response.json()

            if header is None:
                header = data["header"]
                index_date = header["date"].replace("/", "-")

                if path:
                    full_path = os.path.join(path, f"{index}_{index_date}.json")
                    if not overwrite and os.path.exists(full_path):
                        with open(full_path, encoding="utf-8") as arquivo:
                            return json.load(arquivo)

            results = data.get("results", [])
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

    if not header or not every_data:
        raise Exception(f"Data Not Found for {index}")

    index_data = {"header": header, "results": every_data}

    if full_path:
        with open(full_path, "w", encoding="utf-8") as arquivo:
            json.dump(index_data, arquivo, indent=4, ensure_ascii=False)

    return index_data


def download_indexes(
    index_list: list[B3Index | str], path: str | None = None, overwrite: bool = False
):
    """Extracts JSON files from a list of B3 indices"""
    indexes_data = {}

    for i in tqdm(index_list, desc="Download B3"):
        if i not in VALID_INDEXES:
            tqdm.write(f"Index {i} Not Found")
            continue
        try:
            indexes_data[str(i)] = download_index(
                index=i, path=path, overwrite=overwrite
            )
        except Exception as e:
            tqdm.write(str(e))

    return indexes_data
