# gc2web/SourceMixin.py
from typing import List
from Source import Source
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags

class SourcesMixin:
    def __init__(self):
        self.__source_ids: List[str] = []
        self.__sources_cache: List[Source] | None = None

    def parse_sources(self, line: GedcomLine):
        from GedcomTransmission import GedcomTransmission

        for subline in GedcomTransmission().iterate(line, tag=GedcomTags.SOUR):
            if subline.pointer_value:
                self.__source_ids.append(subline.pointer_value)
                
    @property
    def sources(self) -> List[Source]:
        from GedcomTransmission import GedcomTransmission

        if self.__sources_cache is None:
            self.__sources_cache = list(filter(None, (GedcomTransmission().get_source(source_id) for source_id in self.__source_ids)))
        return self.__sources_cache

    def add_source(self, source: Source):
        self.__source_ids.append(source.xref_id)
