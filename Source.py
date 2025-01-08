from typing import Optional
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags

class Source:
    def __init__(self, transmission: 'GedcomTransmission'): # type: ignore
        self.__xref_id: str = ""
        self.__transmission: 'GedcomTransmission' = transmission # type: ignore
        self.__title: str | None = None
        self.__author: str | None = None
        self.__publication: str | None = None
        self.__text: str | None = None

    def parse(self, line: GedcomLine) -> 'Source':
        """Parse a source from a GEDCOM line"""
        if not line.xref_id:
            raise ValueError(f"Source has no xref_id: {line}")
        self.__xref_id = line.xref_id

        for subline in self.__transmission.iterate(line):
            if subline.tag == GedcomTags.TITL:
                self.title = subline.value
            elif subline.tag == GedcomTags.AUTH:
                self.author = subline.value
            elif subline.tag == GedcomTags.PUBL:
                self.publication = subline.value
            elif subline.tag == GedcomTags.TEXT:
                self.text = subline.value

        return self

    @property
    def xref_id(self) -> str:
        return self.__xref_id
    
    @xref_id.setter
    def xref_id(self, value: str):
        self.__xref_id = value

    @property
    def transmission(self) -> 'GedcomTransmission': # type: ignore
        return self.__transmission
    
    @transmission.setter
    def transmission(self, value: 'GedcomTransmission'): # type: ignore
        self.__transmission = value
   
    @property
    def title(self) -> str | None:
        return self.__title

    @title.setter
    def title(self, value: str | None):
        self.__title = value

    @property
    def author(self) -> str | None:
        return self.__author

    @author.setter
    def author(self, value: str | None):
        self.__author = value

    @property
    def publication(self) -> str | None:
        return self.__publication

    @publication.setter
    def publication(self, value: str | None):
        self.__publication = value

    @property
    def text(self) -> str | None:
        return self.__text

    @text.setter
    def text(self, value: str | None):
        self.__text = value

    def __repr__(self) -> str:
        return f"Source(xref_id={self.xref_id}, title={self.title})"
