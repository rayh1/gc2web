from parser.GedcomLine import GedcomLine
from parser.GedcomTags import GedcomTags
from parser.GedcomParser import GedcomParser

class Repository:
    def __init__(self):
        self.__xref_id: str = ""
        self.__name: str | None = None
        self.__www: str | None = None

    def parse(self, line: GedcomLine) -> 'Repository':
        from model.GedcomTransmission import GedcomTransmission

        """Parse a repository from a GEDCOM line"""
        if not line.xref_id:
            raise ValueError(f"Repository has no xref_id: {line}")
        self.__xref_id = line.xref_id

        for subline in GedcomParser().iterate(line):
            if subline.tag == GedcomTags.NAME:
                self.name = subline.value
            elif subline.tag == GedcomTags.WWW:
                self.www = subline.value

        return self

    @property
    def xref_id(self) -> str:
        return self.__xref_id
    
    @xref_id.setter
    def xref_id(self, value: str):
        self.__xref_id = value

    @property
    def name(self) -> str | None:
        return self.__name

    @name.setter
    def name(self, value: str | None):
        self.__name = value

    @property
    def www(self) -> str | None:
        return self.__www

    @www.setter
    def www(self, value: str | None):
        self.__www = value

    def __repr__(self) -> str:
        return f"Repository(xref_id={self.xref_id}, name={self.name})"
