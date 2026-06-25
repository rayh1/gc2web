from model.SourcesMixin import SourcesMixin
from model.NotesMixin import NotesMixin

class Name(SourcesMixin, NotesMixin):
    def __init__(self):
        super().__init__()
        NotesMixin.__init__(self)

        self.__value: str | None = None

    @property
    def value(self) -> str | None:
        return self.__value

    @value.setter
    def value(self, value: str | None):
        self.__value = value

    # Utility methods

    @property
    def plain_value(self) -> str | None:
        if not self.__value:
            return None

        return self.__value.replace("/", "")

    def __str__(self) -> str:
        return self.plain_value if self.plain_value else "?"
