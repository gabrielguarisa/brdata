import os
import base64
import json
import time
from enum import StrEnum
from typing import Any, TypeAlias

import requests
from tqdm import tqdm

B3Payload: TypeAlias = dict[str, Any]
B3IndexesPayload: TypeAlias = dict[str, B3Payload]


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


VALID_INDEXES: set[str] = {index.value for index in B3Index}


def params_to_base64(params: str) -> str:
    """Converts search parameters to base64"""
    original_bytes = params.encode("utf-8")
    encoded_bytes = base64.b64encode(original_bytes)
    encoded_params = encoded_bytes.decode("ascii")
    return encoded_params


def download_index(
    index: B3Index | str, path: str | None = None, overwrite: bool = False
) -> B3Payload:
    """Extracts JSON files from B3 indexes"""
    if index not in VALID_INDEXES:
        raise ValueError(f"Index {index} Not Found")

    if path:
        os.makedirs(path, exist_ok=True)

    all_results: list[dict[str, Any]] = []
    current_page = 1
    header: dict[str, Any] | None = None
    full_path: str | None = None

    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    while True:
        request_params = {
            "language": "pt-br",
            "pageNumber": current_page,
            "pageSize": 100,
            "index": f"{index}",
            "segment": "1",
        }
        request_params_json = json.dumps(request_params)
        encoded_params = params_to_base64(request_params_json)
        url = f"https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/{encoded_params}"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if header is None:
                header = data["header"]
                index_date = header["date"].replace("/", "-")

                if path:
                    full_path = os.path.join(path, f"{index}_{index_date}.json")
                    if not overwrite and os.path.exists(full_path):
                        with open(full_path, encoding="utf-8") as file:
                            return json.load(file)

            results = data.get("results", [])
            if not results:
                break

            all_results.extend(results)

            total_pages = data.get("page", {}).get("totalPages", 0)
            if current_page >= total_pages:
                break

            current_page += 1
            time.sleep(0.5)

        except Exception as error:
            raise Exception(f"Index Error {index}: {error}") from None

    if not header or not all_results:
        raise Exception(f"Data Not Found for {index}")

    index_data = {"header": header, "results": all_results}

    if full_path:
        with open(full_path, "w", encoding="utf-8") as file:
            json.dump(index_data, file, indent=4, ensure_ascii=False)

    return index_data


def download_indexes(
    index_list: list[B3Index | str], path: str | None = None, overwrite: bool = False
) -> B3IndexesPayload:
    """Extracts JSON files from a list of B3 indices"""
    indexes_data: B3IndexesPayload = {}

    for index in tqdm(index_list, desc="Download B3"):
        try:
            indexes_data[str(index)] = download_index(
                index=index, path=path, overwrite=overwrite
            )
        except Exception as error:
            tqdm.write(str(error))

    return indexes_data
