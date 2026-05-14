import os
import base64
import json
import time
from datetime import datetime
from enum import StrEnum
from typing import Any, TypeAlias
from urllib.parse import urljoin

import requests
from tqdm import tqdm

B3Payload: TypeAlias = dict[str, Any]
B3IndexesPayload: TypeAlias = dict[str, B3Payload]
B3Rows: TypeAlias = list[dict[str, Any]]
THEORETICAL_PORTFOLIO_URL = (
    "https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/"
    "GetTheoricalPortfolio/"
)
DAY_PORTFOLIO_URL = (
    "https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/"
)


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


def list_indexes() -> list[str]:
    """Lists available B3 indexes."""
    return [index.value for index in B3Index]


def params_to_base64(params: str) -> str:
    """Converts search parameters to base64"""
    original_bytes = params.encode("utf-8")
    encoded_bytes = base64.b64encode(original_bytes)
    encoded_params = encoded_bytes.decode("ascii")
    return encoded_params


def _format_date_to_iso(date: str) -> str:
    for date_format in ("%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(date, date_format).date().isoformat()
        except ValueError:
            continue

    raise ValueError(f"Invalid B3 date format: {date}")


def _request_index_page(
    index_code: str,
    page_number: int,
    base_url: str,
    include_segment: bool = False,
) -> B3Payload:
    request_params = {
        "language": "en-us",
        "pageNumber": page_number,
        "pageSize": 100,
        "index": index_code,
    }
    if include_segment:
        request_params["segment"] = "1"

    request_params_json = json.dumps(request_params)
    encoded_params = params_to_base64(request_params_json)

    headers: dict[str, str] = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(urljoin(base_url, encoded_params), headers=headers)
    response.raise_for_status()
    return response.json()


def _parse_index_page(data: B3Payload) -> tuple[dict[str, Any] | None, B3Rows, int]:
    header = data.get("header")
    results = data.get("results", [])
    total_pages = data.get("page", {}).get("totalPages", 0)
    return header, results, total_pages


def _fetch_index_data(index_code: str, theoretical: bool) -> B3Payload:
    all_results: B3Rows = []
    current_page = 1
    header: dict[str, Any] | None = None
    base_url = THEORETICAL_PORTFOLIO_URL if theoretical else DAY_PORTFOLIO_URL

    while True:
        try:
            data = _request_index_page(
                index_code,
                current_page,
                base_url=base_url,
                include_segment=not theoretical,
            )
            page_header, results, total_pages = _parse_index_page(data)

            if header is None:
                header = page_header

            if not results:
                break

            all_results.extend(results)

            if current_page >= total_pages:
                break

            current_page += 1
            time.sleep(0.5)

        except Exception as error:
            raise Exception(f"Index Error {index_code}: {error}") from None

    if not all_results:
        raise Exception(f"Data Not Found for {index_code}")

    index_data: B3Payload = {"results": all_results}
    if not theoretical:
        if not header or "date" not in header:
            raise Exception(f"Date Not Found for {index_code}")
        index_data["date"] = _format_date_to_iso(header["date"])

    return index_data


def download_index(
    index: B3Index | str,
    path: str | None = None,
    overwrite: bool = False,
    theoretical: bool = True,
) -> B3Payload:
    """Extracts JSON files from B3 indexes"""
    index_code = str(index).upper()

    if index_code not in VALID_INDEXES:
        raise ValueError(f"Index {index} Not Found")

    if path:
        os.makedirs(path, exist_ok=True)

    file_name = f"{index_code}.json" if theoretical else f"{index_code}_day.json"
    full_path = os.path.join(path, file_name) if path else None

    if full_path and not overwrite and os.path.exists(full_path):
        with open(full_path, encoding="utf-8") as file:
            return json.load(file)

    index_data = _fetch_index_data(index_code, theoretical=theoretical)

    if full_path:
        with open(full_path, "w", encoding="utf-8") as file:
            json.dump(index_data, file, indent=4, ensure_ascii=False)

    return index_data


def download_indexes(
    index_list: list[B3Index | str],
    path: str | None = None,
    overwrite: bool = False,
    theoretical: bool = True,
) -> B3IndexesPayload:
    """Extracts JSON files from a list of B3 indices"""
    indexes_data: B3IndexesPayload = {}

    for index in tqdm(index_list, desc="Download B3"):
        index_code = str(index).upper()
        try:
            indexes_data[index_code] = download_index(
                index=index, path=path, overwrite=overwrite, theoretical=theoretical
            )
        except Exception as error:
            tqdm.write(str(error))

    return indexes_data


__all__ = ["B3Index", "list_indexes", "download_index", "download_indexes"]
