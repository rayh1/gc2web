from typing import TypeVar
from Source import Source
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags

class Name:
    def __init__(self, transmission: 'GedcomTransmission', value: str | None = None): # type: ignore
        self.__transmission: 'GedcomTransmission' = transmission # type: ignore
        self.__value: str | None = value
        self.__source_ids: list[str] = []

        self.__sources_cache: list[Source] | None = None
        
    @classmethod
    def parse(cls: type, transmission: 'GedcomTransmission', line: GedcomLine) -> type: # type: ignore
        """Parse a name from a GEDCOM line"""
        name = cls(transmission, line.value)
        for subline in transmission.iterate(line, tag=GedcomTags.SOUR):
            if subline.pointer_value:
                name.source_ids.append(subline.pointer_value)
        
        return name

    @property
    def transmission(self) -> 'GedcomTransmission': # type: ignore
        return self.__transmission
    
    @transmission.setter
    def transmission(self, value: 'GedcomTransmission'): # type: ignore
        self.__transmission = value

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
        if self.__sources_cache is None:
            self.__sources_cache = [self.transmission.get_source(source_id) for source_id in self.source_ids]
        return self.__sources_cache

    def __str__(self) -> str:
        return self.__value.replace("/", "") if self.__value else "?"
