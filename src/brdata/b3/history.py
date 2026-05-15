import datetime as dt
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests

COTAHIST_BASE_URL = "https://bvmf.bmfbovespa.com.br/InstDados/SerHist"
DEFAULT_COTAHIST_PATH = "data/landing/b3/cotahist"
COTAHIST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    ),
    "Accept": "application/zip,application/octet-stream,*/*",
}


@dataclass(frozen=True)
class CotahistFile:
    series: str
    ref: str
    filename: str

    @property
    def url(self) -> str:
        return f"{COTAHIST_BASE_URL}/{self.filename}"

    @property
    def txt_filename(self) -> str:
        return self.filename.removesuffix(".ZIP") + ".TXT"


def annual_file(year: int) -> CotahistFile:
    """Returns metadata for a yearly COTAHIST file."""
    return CotahistFile(
        series="annual",
        ref=str(year),
        filename=f"COTAHIST_A{year}.ZIP",
    )


def monthly_file(year: int, month: int) -> CotahistFile:
    """Returns metadata for a monthly COTAHIST file."""
    _validate_month(month)
    return CotahistFile(
        series="monthly",
        ref=f"{year}-{month:02d}",
        filename=f"COTAHIST_M{month:02d}{year}.ZIP",
    )


def daily_file(date: dt.date | str) -> CotahistFile:
    """Returns metadata for a daily COTAHIST file."""
    date = _parse_date(date)
    return CotahistFile(
        series="daily",
        ref=date.isoformat(),
        filename=f"COTAHIST_D{date:%d%m%Y}.ZIP",
    )


def is_zip_file(path: str | Path) -> bool:
    """Checks whether a path points to a valid ZIP file."""
    path = Path(path)
    if not path.exists() or path.stat().st_size < 4:
        return False

    with path.open("rb") as file:
        magic = file.read(4)

    return magic == b"PK\x03\x04" and zipfile.is_zipfile(path)


def download_file(
    item: CotahistFile,
    output_dir: str | Path = DEFAULT_COTAHIST_PATH,
    overwrite: bool = False,
    validate_zip: bool = True,
    timeout: int = 60,
) -> Path | None:
    """Downloads a COTAHIST file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / item.filename

    if output_path.exists() and not overwrite:
        if not validate_zip or is_zip_file(output_path):
            return output_path

    tmp_path = output_path.with_suffix(output_path.suffix + ".part")

    try:
        with requests.get(
            item.url,
            headers=COTAHIST_HEADERS,
            stream=True,
            timeout=timeout,
        ) as response:
            if response.status_code == 404:
                return None

            response.raise_for_status()
            if _is_html_response(response):
                return None

            total_bytes = _write_response_content(response, tmp_path)
            if total_bytes == 0:
                tmp_path.unlink(missing_ok=True)
                return None

            tmp_path.replace(output_path)

            if validate_zip and not is_zip_file(output_path):
                output_path.unlink(missing_ok=True)
                return None

            return output_path

    except requests.RequestException:
        tmp_path.unlink(missing_ok=True)
        return None


def download_annual_series(
    year: int,
    output_dir: str | Path = f"{DEFAULT_COTAHIST_PATH}/annual",
    overwrite: bool = False,
    validate_zip: bool = True,
    timeout: int = 60,
) -> Path | None:
    """Downloads the yearly COTAHIST series for a year."""
    return download_file(
        item=annual_file(year),
        output_dir=output_dir,
        overwrite=overwrite,
        validate_zip=validate_zip,
        timeout=timeout,
    )


def download_monthly_series(
    year: int,
    month: int,
    output_dir: str | Path = f"{DEFAULT_COTAHIST_PATH}/monthly",
    overwrite: bool = False,
    validate_zip: bool = True,
    timeout: int = 60,
) -> Path | None:
    """Downloads the monthly COTAHIST series for a month."""
    return download_file(
        item=monthly_file(year, month),
        output_dir=output_dir,
        overwrite=overwrite,
        validate_zip=validate_zip,
        timeout=timeout,
    )


def download_daily_series(
    date: dt.date | str,
    output_dir: str | Path = f"{DEFAULT_COTAHIST_PATH}/daily",
    overwrite: bool = False,
    validate_zip: bool = True,
    timeout: int = 60,
) -> Path | None:
    """Downloads the daily COTAHIST series for a date."""
    return download_file(
        item=daily_file(date),
        output_dir=output_dir,
        overwrite=overwrite,
        validate_zip=validate_zip,
        timeout=timeout,
    )


def iter_months(
    start_year: int,
    start_month: int,
    end_year: int,
    end_month: int,
) -> Iterable[tuple[int, int]]:
    """Iterates over months in a closed interval."""
    _validate_month(start_month)
    _validate_month(end_month)
    current = dt.date(start_year, start_month, 1)
    end = dt.date(end_year, end_month, 1)

    if current > end:
        raise ValueError("Start month cannot be greater than end month")

    while current <= end:
        yield current.year, current.month

        if current.month == 12:
            current = dt.date(current.year + 1, 1, 1)
        else:
            current = dt.date(current.year, current.month + 1, 1)


def iter_dates(
    start_date: dt.date | str,
    end_date: dt.date | str,
    weekdays_only: bool = False,
) -> Iterable[dt.date]:
    """Iterates over dates in a closed interval."""
    start_date = _parse_date(start_date)
    end_date = _parse_date(end_date)

    if start_date > end_date:
        raise ValueError("Start date cannot be greater than end date")

    current = start_date

    while current <= end_date:
        if not weekdays_only or current.weekday() < 5:
            yield current

        current += dt.timedelta(days=1)


def download_annual_series_range(
    start_year: int,
    end_year: int,
    output_dir: str | Path = f"{DEFAULT_COTAHIST_PATH}/annual",
    overwrite: bool = False,
    validate_zip: bool = True,
    timeout: int = 60,
    sleep: float = 1.0,
) -> list[Path]:
    """Downloads yearly COTAHIST series within a year range."""
    if start_year > end_year:
        raise ValueError("Start year cannot be greater than end year")

    downloaded: list[Path] = []

    for year in range(start_year, end_year + 1):
        path = download_annual_series(
            year=year,
            output_dir=output_dir,
            overwrite=overwrite,
            validate_zip=validate_zip,
            timeout=timeout,
        )

        if path is not None:
            downloaded.append(path)

        _sleep(sleep)

    return downloaded


def download_monthly_series_range(
    start_year: int,
    start_month: int,
    end_year: int,
    end_month: int,
    output_dir: str | Path = f"{DEFAULT_COTAHIST_PATH}/monthly",
    overwrite: bool = False,
    validate_zip: bool = True,
    timeout: int = 60,
    sleep: float = 1.0,
) -> list[Path]:
    """Downloads monthly COTAHIST series within a month range."""
    downloaded: list[Path] = []

    for year, month in iter_months(start_year, start_month, end_year, end_month):
        path = download_monthly_series(
            year=year,
            month=month,
            output_dir=output_dir,
            overwrite=overwrite,
            validate_zip=validate_zip,
            timeout=timeout,
        )

        if path is not None:
            downloaded.append(path)

        _sleep(sleep)

    return downloaded


def download_daily_series_range(
    start_date: dt.date | str,
    end_date: dt.date | str,
    output_dir: str | Path = f"{DEFAULT_COTAHIST_PATH}/daily",
    weekdays_only: bool = True,
    overwrite: bool = False,
    validate_zip: bool = True,
    timeout: int = 60,
    sleep: float = 1.0,
) -> list[Path]:
    """Downloads daily COTAHIST series within a date range."""
    downloaded: list[Path] = []

    for date in iter_dates(start_date, end_date, weekdays_only=weekdays_only):
        path = download_daily_series(
            date=date,
            output_dir=output_dir,
            overwrite=overwrite,
            validate_zip=validate_zip,
            timeout=timeout,
        )

        if path is not None:
            downloaded.append(path)

        _sleep(sleep)

    return downloaded


def _parse_date(date: dt.date | str) -> dt.date:
    if isinstance(date, str):
        return dt.date.fromisoformat(date)
    return date


def _validate_month(month: int) -> None:
    if not 1 <= month <= 12:
        raise ValueError("month must be between 1 and 12")


def _is_html_response(response: requests.Response) -> bool:
    content_type = response.headers.get("content-type", "").lower()
    return "html" in content_type


def _write_response_content(response: requests.Response, output_path: Path) -> int:
    total_bytes = 0

    with output_path.open("wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)
                total_bytes += len(chunk)

    return total_bytes


def _sleep(seconds: float) -> None:
    if seconds > 0:
        time.sleep(seconds)


__all__ = [
    "CotahistFile",
    "annual_file",
    "monthly_file",
    "daily_file",
    "is_zip_file",
    "download_file",
    "download_annual_series",
    "download_monthly_series",
    "download_daily_series",
    "iter_months",
    "iter_dates",
    "download_annual_series_range",
    "download_monthly_series_range",
    "download_daily_series_range",
]
