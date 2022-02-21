from typing import List, Union

import datetime
import glob
import os
from io import BytesIO
from zipfile import ZipFile

import pandas as pd
from cachier import cachier

from brdata.utils import CACHE_DIR, get_response, remove_empty_str

from ._utils import (
    METADATA_EXTENSIONS,
    get_data_urls,
    get_metadata_urls,
    get_table_links,
)


def convert_metadata_to_dataframe(filename: str) -> pd.DataFrame:
    """Converte um arquivo de metadata em um dataframe"""
    with open(filename, "r", encoding="latin1") as f:
        data = f.read()

    variables = {}
    last_var = None
    line_trigger = False
    for line in filter(None, data.split("\n")):
        if line[0] == "-":
            line_trigger = not line_trigger
        else:
            key, value = line.split(":")
            if line_trigger:
                value = remove_empty_str(value)
                variables[value] = {}
                last_var = value
            else:
                variables[last_var][remove_empty_str(key)] = remove_empty_str(value)

    return pd.DataFrame(variables).T.reset_index().rename(columns={"index": "Nome"})


@cachier(stale_after=datetime.timedelta(days=1), cache_dir=CACHE_DIR)
def download_metadata(folder: str, to_dataframe: bool = True) -> List[str]:
    """Baixa os arquivos de metadata da cvm"""
    base_path = os.path.join(folder, "cvm/metadata/")
    for name, url in get_metadata_urls().items():
        extension = METADATA_EXTENSIONS[name]
        links = get_table_links(url, extension, as_dict=False)
        full_path = os.path.join(base_path, name)
        for link in links:
            os.makedirs(full_path, exist_ok=True)
            if extension == ".zip":
                with ZipFile(BytesIO(get_response(link).content)) as zip:
                    zip.extractall(full_path)
            elif extension == ".txt":
                filename = os.path.join(full_path, link.split("/")[-1])
                with open(filename, "wb") as f:
                    f.write(get_response(link).content)

    all_filenames = glob.glob(os.path.join(base_path, "*/*.txt"))

    if to_dataframe:
        csv_filenames = []
        for filename in all_filenames:
            csv_filenames.append(filename.replace(".txt", ".csv"))
            convert_metadata_to_dataframe(filename).to_csv(
                csv_filenames[-1], index=False
            )
            os.remove(filename)

        return csv_filenames

    return all_filenames


@cachier(stale_after=datetime.timedelta(days=1), cache_dir=CACHE_DIR)
def download_data(folder: str, names: Union[str, List[str]] = None) -> List[str]:
    """Baixa os arquivos de dados da cvm"""
    all_filenames = []
    urls = get_data_urls()

    if names is None:
        names = list(urls.keys())
    elif isinstance(names, str):
        names = [names]

    names = [name.lower() for name in names]

    base_path = os.path.join(folder, "cvm/data/")
    for name, url in urls.items():
        if name in names:
            links = get_table_links(url, as_dict=False)
            for link in links:
                full_path = os.path.join(base_path, name)
                os.makedirs(full_path, exist_ok=True)

                response = get_response(link)

                with ZipFile(BytesIO(response.content)) as zip:
                    filenames = zip.namelist()

                    for filename in filenames:
                        if filename.endswith(".csv"):
                            try:
                                final_filename = os.path.join(full_path, filename)
                                df = pd.read_csv(
                                    zip.open(filename), delimiter=";", encoding="latin1"
                                )
                                df.to_csv(final_filename, index=False)
                                all_filenames.append(final_filename)
                            except Exception as e:
                                print("Invalid file", final_filename, e)
    return all_filenames
