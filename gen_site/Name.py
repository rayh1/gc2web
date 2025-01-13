from GedcomLine import GedcomLine
from SourcesMixin import SourcesMixin

class Name(SourcesMixin):
    def __init__(self):
        super().__init__()
        
        self.__value: str | None = None

    def parse(self, line: GedcomLine) -> 'Name':
        """Parse a name from a GEDCOM line"""
        self.__value = line.value
        self.parse_sources(line)        
        
        return self

    @property
    def value(self) -> str | None:
        return self.__value

    @value.setter
    def value(self, value: str | None):
        self.__value = value

    # Utility methods

    def __str__(self) -> str:
        return self.__value.replace("/", "") if self.__value else "?"
