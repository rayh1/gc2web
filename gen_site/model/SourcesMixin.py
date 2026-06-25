from typing import List
from model.Source import Source

class SourcesMixin:
    def __init__(self):
        self.__source_ids: List[str] = []
        self.__sources_cache: List[Source] | None = None

    @property
    def sources(self) -> List[Source]:
        from model.GedcomModel import GedcomModel

        if self.__sources_cache is None:
            self.__sources_cache = list(filter(None, (GedcomModel().get_source(source_id) for source_id in self.__source_ids)))
        return self.__sources_cache

    @property
    def source_ids(self) -> List[str]:
        return self.__source_ids

    def add_source_id(self, source_id: str):
        self.__sources_cache = None
        self.__source_ids.append(source_id)
