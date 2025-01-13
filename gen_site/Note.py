from GedcomLine import GedcomLine

class Note:
    def __init__(self):
        self.__value: str | None = None

    def parse(self, line: GedcomLine) -> 'Note':

        self.__value = line.value

        return self

    @property
    def value(self) -> str | None:
        return self.__value

    @value.setter
    def value(self, value: str | None):
        self.__value = value

    def __repr__(self) -> str:
        return f"Note(xref_id=text={self.value})"
