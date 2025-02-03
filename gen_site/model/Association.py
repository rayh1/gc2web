from typing import Union

from parser.GedcomLine import GedcomLine
from parser.GedcomTags import GedcomTags
from parser.GedcomParser import GedcomParser

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

    def parse(self, line: GedcomLine) -> 'Association':
        from model.GedcomTransmission import GedcomTransmission

        if not line.pointer_value:
            raise ValueError(f"Association has no pointer value: {line}")

        self.__line_num = line.line_num
        self.__individual_id = line.pointer_value

        for subline in GedcomParser().iterate(line):
            if subline.tag == GedcomTags.RELA and subline.value:
                parts: list[str] = subline.value.split(' ')
                self.__rel_desc = parts[0] if len(parts) > 1 else subline.value
                self.__rel_type = parts[1] if len(parts) > 1 else None
        
        self.parse_sources(line)
        self.parse_notes(line)

        return self

    @property
    def individual_id(self) -> str | None:
        return self.__individual_id

    @property
    def rel_desc(self) -> str | None:
        return self.__rel_desc

    @property
    def rel_type(self) -> str | None:
        return self.__rel_type

    @property
    def line_num(self) -> int | None:
        return self.__line_num
    
# Utility
    def individual(self) -> Union['Individual', None]: # type: ignore
        from GedcomTransmission import GedcomTransmission

        if not self.individual_id:
            return None

        return GedcomTransmission().get_individual(self.individual_id)
