from typing import Optional

class Source:
    def __init__(self, xref_id: str, transmission: 'GedcomTransmission', title: str  | None = None, author: str | None = None, publication: str | None = None, text: str | None = None): # type: ignore
        self.__xref_id: str = xref_id
        self.__transmission: 'GedcomTransmission' = transmission # type: ignore
        self.__title: str | None = title
        self.__author: str | None = author
        self.__publication: str | None = publication
        self.__text: str | None = text

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
