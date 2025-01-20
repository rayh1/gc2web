from datetime import datetime
import re

class Date:
    def __init__(self, value: str | None = None):
        self.__value: str | None = value
        self.__parsed_value: str | tuple[str | None, str | None] | None = None

    @property
    def value(self) -> str | None:
        return self.__value

    @value.setter
    def value(self, value: str | None):
        self.__value = value

    def __str__(self) -> str:
        return self.pretty_str()

    def date(self) -> datetime | None:
        parsed_value = self.parse()

        if isinstance(parsed_value, tuple):
            parsed_value = parsed_value[0]

        if not parsed_value:
            return None

        try:
            return datetime.strptime(parsed_value, "%d %b %Y")
        except ValueError:
            pass
        try:
            return datetime.strptime(parsed_value, "%b %Y")
        except ValueError:
            pass
        try:
            return datetime.strptime(parsed_value, "%Y")
        except ValueError:
            pass

        return None
    
    def pretty_str(self) -> str:
        parsed_value = self.parse()
        if not parsed_value:
            return "?"
        
        if isinstance(parsed_value, tuple):
            return f"{parsed_value[0] or '?'} - {parsed_value[1] or '?'}"
        
        return parsed_value


    DATE_FORMAT_RE = r"(\d{4}|\w{3} \d{4}|\d{1,2} \w{3} \d{4})"

    def parse(self) -> str | tuple[str | None, str | None] | None:
        if self.__parsed_value:
            return self.__parsed_value
        
        if not self.__value:
            return None

        PARSERS = [
            self.parse_period_date,
            self.parse_range_date,
            self.parse_approximated_date,
            self.parse_int_date,
            self.parse_simple_date,
        ]

        for parser in PARSERS:
            parsed_value = parser(self.__value)
            if parsed_value:
                self.__parsed_value = parsed_value
                return parsed_value

        return None

    @staticmethod
    def parse_simple_date(value: str) -> str | None:
        match = re.search(Date.DATE_FORMAT_RE, value)
        if match:
            return match.group(1)
        
        return None

    @staticmethod
    def parse_period_date(value: str) -> tuple[str | None, str | None] | None:
        match = re.search(r"FROM " + Date.DATE_FORMAT_RE + " TO " + Date.DATE_FORMAT_RE, value)
        if match:
            return match.group(1), match.group(2)

        match = re.search(r"FROM " + Date.DATE_FORMAT_RE, value)
        if match:
            return match.group(1), None
        
        match = re.search(r"TO " + Date.DATE_FORMAT_RE, value)
        if match:
            return None, match.group(1)

        return None

    @staticmethod
    def parse_range_date(value: str) -> str | None:
        match = re.search(r"BET " + Date.DATE_FORMAT_RE, value)
        return match.group(1) if match else None

    @staticmethod
    def parse_approximated_date(value: str) -> str | None:
        match = re.search(r"(ABT|CAL|EST) " + Date.DATE_FORMAT_RE, value)
        return match.group(2) if match else None

    @staticmethod
    def parse_int_date(value: str) -> str | None:
        match = re.search(r"INT " + Date.DATE_FORMAT_RE, value)
        return match.group(1) if match else None
