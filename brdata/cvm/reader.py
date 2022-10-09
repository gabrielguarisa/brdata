import typing

import pandas as pd

from . import download, processors


class Reader:
    def __init__(
        self, prefix: str = None, data: typing.Dict[str, pd.DataFrame] = None
    ) -> None:
        _dfs = {}
        self._processors = {}
        self._years = []

        if prefix is not None:
            data = download.get_data(prefix)

        for filename in list(data.keys()):
            original_form_name = filename[:-5]
            year = int(filename[-4:])

            if year not in self._years:
                self._years.append(year)

            if original_form_name not in _dfs:
                _dfs[original_form_name] = []

            _dfs[original_form_name].append(data[filename])

        for original_form_name, group in _dfs.items():
            calc_prefix = original_form_name.split("_")[0]
            form_name = original_form_name[len(calc_prefix) + 1 :]

            self._processors[form_name] = processors.get_processor(
                calc_prefix.lower(), form_name.lower(), group
            )

        self._years.sort()

    @property
    def processors(self) -> typing.Dict[str, processors.Processor]:
        return self._processors

    @property
    def years(self) -> typing.List[int]:
        return self._years

    @property
    def forms(self) -> typing.List[str]:
        return list(self._processors.keys())

    def get_data(self, form_name: str) -> pd.DataFrame:
        if form_name not in self.processors:
            raise ValueError(
                f"Form {form_name} not found. Available forms: {self.forms}"
            )

        return self.processors[form_name].data
