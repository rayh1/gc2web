from Source import Source
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags

class Name:
    def __init__(self):
        self.__value: str | None = None
        self.__source_ids: list[str] = []

        self.__sources_cache: list[Source] | None = None

    def parse(self, line: GedcomLine) -> 'Name':
        from GedcomTransmission import GedcomTransmission

        """Parse a name from a GEDCOM line"""
        self.__value = line.value
        
        for subline in GedcomTransmission().iterate(line, tag=GedcomTags.SOUR):
            if subline.pointer_value:
                self.__source_ids.append(subline.pointer_value)
        
        return self

    @property
    def value(self) -> str | None:
        return self.__value

    @value.setter
    def value(self, value: str | None):
        self.__value = value

    @property
    def source_ids(self) -> list[str]:
        return self.__source_ids

    @source_ids.setter
    def source_ids(self, source_ids: list[str]):
        self.__source_ids = source_ids

    # Utility methods

    @property
    def sources(self) -> list[Source]:
        from GedcomTransmission import GedcomTransmission

        if self.__sources_cache is None:
            self.__sources_cache = list(filter(None, (GedcomTransmission().get_source(source_id) for source_id in self.source_ids)))
        return self.__sources_cache

    def __str__(self) -> str:
        return self.__value.replace("/", "") if self.__value else "?"
