from typing import Optional

class Source:
    def __init__(self, xref_id: str, transmission: 'GedcomTransmission', title: str = "", author: str = "", publication: str = "", text: str = ""): # type: ignore
        self._xref_id: str = xref_id
        self._transmission: 'GedcomTransmission' = transmission # type: ignore
        self._title: str = title
        self._author: str = author
        self._publication: str = publication
        self._text: str = text

    @property
    def xref_id(self) -> str:
        return self._xref_id

    @property
    def transmission(self) -> 'GedcomTransmission': # type: ignore
        return self._transmission

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value

    @property
    def author(self) -> str:
        return self._author

    @author.setter
    def author(self, value: str) -> None:
        self._author = value

    @property
    def publication(self) -> str:
        return self._publication

    @publication.setter
    def publication(self, value: str) -> None:
        self._publication = value

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value

    def __repr__(self) -> str:
        return f"Source(xref_id={self.xref_id}, title={self.title})"
