from GedcomLine import GedcomLine
from GedcomTags import GedcomTags
from Repository import Repository

class Source:
    def __init__(self):
        self.__xref_id: str = ""
        self.__title: str | None = None
        self.__author: str | None = None
        self.__publication: str | None = None
        self.__text: str | None = None
        self.__repository_id: str | None = None
        self.__repository_cache: Repository | None = None

    def parse(self, line: GedcomLine) -> 'Source':
        from GedcomTransmission import GedcomTransmission

        """Parse a source from a GEDCOM line"""
        if not line.xref_id:
            raise ValueError(f"Source has no xref_id: {line}")
        self.__xref_id = line.xref_id

        for subline in GedcomTransmission().iterate(line):
            if subline.tag == GedcomTags.TITL:
                self.title = subline.value
            elif subline.tag == GedcomTags.AUTH:
                self.author = subline.value
            elif subline.tag == GedcomTags.PUBL:
                self.publication = subline.value
            elif subline.tag == GedcomTags.TEXT:
                self.text = subline.value
            elif subline.tag == GedcomTags.REPO:
                self.repository_id = subline.pointer_value

        return self

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
            from GedcomTransmission import GedcomTransmission
            self.__repository_cache = GedcomTransmission().get_repository(self.repository_id)
        return self.__repository_cache

    def __repr__(self) -> str:
        return f"Source(xref_id={self.xref_id}, title={self.title})"

    @property
    def publications(self) -> list[str]:
        from GedcomParser import GedcomParser
        return list(filter(None, self.__publication.split(GedcomParser.CONT_SEP))) if self.__publication else []