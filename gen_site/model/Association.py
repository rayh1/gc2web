from typing import Union

from model.NotesMixin import NotesMixin
from model.SourcesMixin import SourcesMixin

class Association(SourcesMixin, NotesMixin):
    def __init__(self):
        super().__init__()
        NotesMixin.__init__(self)

        self.__line_num: int | None = None
        self.__individual_id: str | None = None
        self.__rel_desc: str | None = None
        self.__rel_type: str | None = None

# Properties

    @property
    def line_num(self) -> int | None:
        return self.__line_num

    @line_num.setter
    def line_num(self, value: int | None):
        self.__line_num = value

    @property
    def individual_id(self) -> str | None:
        return self.__individual_id

    @individual_id.setter
    def individual_id(self, value: str | None):
        self.__individual_id = value

    @property
    def rel_desc(self) -> str | None:
        return self.__rel_desc

    @rel_desc.setter
    def rel_desc(self, value: str | None):
        self.__rel_desc = value

    @property
    def rel_type(self) -> str | None:
        return self.__rel_type

    @rel_type.setter
    def rel_type(self, value: str | None):
        self.__rel_type = value

# Utility

    def individual(self) -> Union['Individual', None]: # type: ignore
        from model.GedcomModel import GedcomModel

        if not self.individual_id:
            return None

        return GedcomModel().get_individual(self.individual_id)
