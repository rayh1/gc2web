import re
from typing import Any

import yaml

GEDCOM_XREF_VALUE_RE = re.compile(r"(:\s*)(@[^@\s\n]+@)(?=\s*(?:#.*)?$)", re.MULTILINE)


class Note:
    def __init__(self) -> None:
        self.__line_num: int | None = None
        self.__value: str | None = None

    @property
    def value(self) -> str | None:
        return self.__value

    @value.setter
    def value(self, value: str | None) -> None:
        self.__value = value

    @property
    def line_num(self) -> int | None:
        return self.__line_num

    @line_num.setter
    def line_num(self, value: int | None) -> None:
        self.__line_num = value

    def __repr__(self) -> str:
        return f"Note(xref_id=text={self.value}, line_num={self.__line_num})"

    def is_yaml(self) -> bool:
        if not self.value:
            return False
        return self.value.strip().startswith("---")

    def parse_yaml(self) -> dict[str, Any] | None:
        value = self.value
        if value is None or not self.is_yaml():
            return None
        try:
            normalized_value = GEDCOM_XREF_VALUE_RE.sub(r'\1"\2"', value)
            data: dict[str, Any] | None = yaml.safe_load(normalized_value)
            return data
        except yaml.YAMLError:
            print(f"Error parsing yaml: {self.value}")
            return None

    def is_private(self) -> bool:
        data = self.parse_yaml()
        if data and "private" in data:
            return bool(data["private"])

        return False
