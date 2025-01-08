import re
from typing import List, Dict
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags
from Individual import Individual
from Family import Family
from Source import Source
from singleton import singleton

class GedcomLineIterator:
    def __init__(self, transmission: 'GedcomTransmission', lines: List[GedcomLine], tag:str | None, value_re: str | None, follow_pointers: bool | None = True):
        self.transmission: 'GedcomTransmission' = transmission
        self.lines: List[GedcomLine] = lines
        self.tag: str | None = tag
        self.value_re: str | None = value_re
        self.follow_pointers: bool = follow_pointers if follow_pointers != None else False

        self.cur_index: int = 0

    def __iter__(self):
        return self

    def __next__(self):
        for i, line in enumerate(self.lines[self.cur_index:], start=self.cur_index):
            self.cur_index = i + 1

            if self.tag and self.tag != line.tag:
                continue

            if self.follow_pointers:
                line = self.transmission.follow_pointers(line)

            if self.value_re != None:
                if line.value == None:
                    continue
                elif re.match(self.value_re, line.value) == None:
                    continue

            return line
                
        raise StopIteration

@singleton
class GedcomTransmission:
    def __init__(self):
        self.__all_lines: List[GedcomLine] = []
        self.__main_lines: List[GedcomLine] = []        
        self.__id_map: dict[str, GedcomLine] = {}
        
        self.__individual_map: Dict[str, Individual] = {}
        self.__family_map: Dict[str, Family] = {}
        self.__source_map: Dict[str, Source] = {}

    @property
    def all_lines(self) -> List[GedcomLine]:
        return self.__all_lines

    @property
    def main_lines(self) -> List[GedcomLine]:
        return self.__main_lines

    @property
    def id_map(self) -> Dict[str, GedcomLine]:
        return self.__id_map

    def iterate(self, line: GedcomLine | None = None, tag: str | None = None, value_re: str | None = None, follow_pointers: bool | None = None) -> GedcomLineIterator:
        """
        Iterate over Gedcom lines based on specified criteria.

        Args:
            line (GedcomLine, optional): Iterate over all sublines of this line. If None, iterate over all lines.
            tag (str, optional): The tag to filter lines by. If None, no tag filtering is applied.
            value_re (str, optional): A regular expression to filter lines by their value. If None, no value filtering is applied.
            follow_pointers (bool, optional): If True, follow pointers during iteration. If None, pointers are not followed.

        Returns:
            GedcomIterator: An iterator over the filtered Gedcom lines.
        """
        if line == None:
            return GedcomLineIterator(self, self.all_lines, tag, value_re, follow_pointers)
        else:
            return GedcomLineIterator(self, line.sublines, tag, value_re, follow_pointers)

    def iterate_id(self, id: str, tag: str | None = None, value_re: str | None = None, follow_pointers: bool | None = None) -> GedcomLineIterator:
        """
        Iterate over Gedcom lines based on specified criteria.

        Args:
            id (GedcomLine, optional): Find a line with this id and iterate over all its sublines.
            tag (str, optional): The tag to filter lines by. If None, no tag filtering is applied.
            value_re (str, optional): A regular expression to filter lines by their value. If None, no value filtering is applied.
            follow_pointers (bool, optional): If True, follow pointers during iteration. If None, pointers are not followed.

        Returns:
            GedcomIterator: An iterator over the filtered Gedcom lines.
        """
        return GedcomLineIterator(self, self.id_map[id].sublines, tag, value_re, follow_pointers)
        
    def follow_pointers(self, line: GedcomLine) -> GedcomLine:
        while line and line.pointer_value:
            line = self.id_map[line.pointer_value]

        return line

    def parse_individuals(self):
        """Parse individuals from the GedcomTransmission"""
        for line in self.iterate(tag=GedcomTags.INDI):
            individual: Individual = Individual().parse(line)                        
            self.__individual_map[individual.xref_id] = individual

    def parse_families(self):
        """Parse families from the GedcomTransmission"""
        for line in self.iterate(tag=GedcomTags.FAM):
            family = Family().parse(line)
            self.__family_map[family.xref_id] = family

    def parse_sources(self):
        """Parse sources from the GedcomTransmission"""
        for line in self.iterate(tag=GedcomTags.SOUR):
            if not line.xref_id:
                continue    # Ignore SOUR line in header
            
            source = Source().parse(line)
            self.__source_map[source.xref_id] = source

    def parse_gedcom(self):
        """Parse the GedcomTransmission and generate all Individual, Family, and Source instances"""
        self.parse_sources()
        self.parse_individuals()
        self.parse_families()

    def get_individual(self, id: str) -> Individual | None:
        return self.__individual_map.get(id, None)
    
    def get_family(self, id: str) -> Family | None:
        return self.__family_map.get(id, None)
    
    def get_source(self, xref_id: str) -> Source | None:
        return self.__source_map.get(xref_id, None)

    @property
    def individuals(self) -> List[Individual]:
        return list(self.__individual_map.values())