import datetime as dt
import io
import zipfile

from brdata.b3 import history


def _zip_bytes(filename: str = "COTAHIST.TXT", content: bytes = b"data") -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zip_file:
        zip_file.writestr(filename, content)
    return buffer.getvalue()


def test_cotahist_file_builders():
    annual = history.annual_file(2026)
    monthly = history.monthly_file(2026, 5)
    daily = history.daily_file("2026-05-15")

    assert annual.filename == "COTAHIST_A2026.ZIP"
    assert annual.txt_filename == "COTAHIST_A2026.TXT"
    assert monthly.filename == "COTAHIST_M052026.ZIP"
    assert daily.filename == "COTAHIST_D15052026.ZIP"
    assert daily.ref == "2026-05-15"


def test_iter_months_returns_closed_interval():
    months = list(history.iter_months(2025, 11, 2026, 2))

    assert months == [(2025, 11), (2025, 12), (2026, 1), (2026, 2)]


def test_iter_dates_skips_weekends_when_requested():
    dates = list(history.iter_dates("2026-05-15", "2026-05-18", weekdays_only=True))

    assert dates == [dt.date(2026, 5, 15), dt.date(2026, 5, 18)]


def test_download_file_writes_valid_zip(tmp_path, mocker):
    response = mocker.Mock()
    response.__enter__ = mocker.Mock(return_value=response)
    response.__exit__ = mocker.Mock(return_value=None)
    response.status_code = 200
    response.headers = {"content-type": "application/zip"}
    response.iter_content.return_value = [_zip_bytes()]

    mock_get = mocker.patch("brdata.b3.history.requests.get", return_value=response)

    path = history.download_file(history.annual_file(2026), output_dir=tmp_path)

    assert path == tmp_path / "COTAHIST_A2026.ZIP"
    assert history.is_zip_file(path)
    mock_get.assert_called_once()


def test_download_file_returns_none_for_404(tmp_path, mocker):
    response = mocker.Mock()
    response.__enter__ = mocker.Mock(return_value=response)
    response.__exit__ = mocker.Mock(return_value=None)
    response.status_code = 404
    response.headers = {}
    mocker.patch("brdata.b3.history.requests.get", return_value=response)

    path = history.download_file(history.annual_file(2026), output_dir=tmp_path)

    assert path is None
