from datetime import datetime
import re

class Date:
    def __init__(self, value: str | None = None):
        self.__value: str | None = value

    @property
    def value(self) -> str | None:
        return self.__value

    @value.setter
    def value(self, value: str | None):
        self.__value = value

    def __str__(self) -> str:
        return self.__value if self.__value else "?"

    def date(self) -> datetime | None:
        if not self.__value:
            return None

        # Simple Gedcom Date format
        try:
            return datetime.strptime(self.__value, "%d %b %Y")
        except ValueError:
            pass

        # Gedcom Date Period (FROM <DATE> TO <DATE>)
        match = re.search(r"FROM (\d{1,2} \w{3} \d{4})", self.__value)
        if match:
            try:
                return datetime.strptime(match.group(1), "%d %b %Y")
            except ValueError:
                pass

        # Gedcom Date Range (BET <DATE> AND <DATE>)
        match = re.search(r"BET (\d{1,2} \w{3} \d{4})", self.__value)
        if match:
            try:
                return datetime.strptime(match.group(1), "%d %b %Y")
            except ValueError:
                pass

        # Gedcom Date Approximated (ABT <DATE>, CAL <DATE>, EST <DATE>)
        match = re.search(r"(ABT|CAL|EST) (\d{1,2} \w{3} \d{4})", self.__value)
        if match:
            try:
                return datetime.strptime(match.group(2), "%d %b %Y")
            except ValueError:
                pass

        # INT <DATE> (<DATE_PHRASE>)
        #match = re.search(r"INT (\d{1,2} \w{3} \d{4})", self.__value)
        match = re.search(r"INT (\d{4})", self.__value)
        if match:
            try:
                return datetime.strptime(match.group(1), "%Y")
            except ValueError:
                pass

        return None
