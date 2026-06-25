import re

from model.Repository import Repository

class Source:
    def __init__(self):
        self.__xref_id: str = ""
        self.__title: str | None = None
        self.__author: str | None = None
        self.__publication: str | None = None
        self.__text: str | None = None
        self.__repository_id: str | None = None
        self.__repository_cache: Repository | None = None

    @property
    def xref_id(self) -> str:
        return self.__xref_id

    @xref_id.setter
    def xref_id(self, value: str):
        self.__xref_id = value

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

    @property
    def repository_id(self) -> str | None:
        return self.__repository_id

    @repository_id.setter
    def repository_id(self, value: str | None):
        self.__repository_id = value

    @property
    def repository(self) -> Repository | None:
        if self.__repository_cache is None and self.repository_id:
            from model.GedcomModel import GedcomModel
            self.__repository_cache = GedcomModel().get_repository(self.repository_id)
        return self.__repository_cache

    def __repr__(self) -> str:
        return f"Source(xref_id={self.xref_id}, title={self.title})"

    @property
    def publications(self) -> list[str]:
        return list(filter(None, re.split(r"\r?\n", self.__publication))) if self.__publication else []
