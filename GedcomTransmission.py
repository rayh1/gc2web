import re
from typing import List, Dict, Tuple
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags
from Individual import Individual
from Family import Family
from Place import Place
from Date import Date
from Name import Name
from Source import Source
from EventDetails import EventDetails

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

    def extract_date_place(self, line: GedcomLine) -> Tuple[Date, Place]:
        """Extract date and place from a GEDCOM event line"""
        date: Date = Date()
        place: Place = Place()
        for subline in self.iterate(line):
            if subline.tag == GedcomTags.DATE:
                date = Date(subline.value)
            elif subline.tag == GedcomTags.PLAC:
                place = Place(subline.value)
        return date, place

    def extract_source_ids(self, line: GedcomLine) -> list[str]:
        """Extract source ids from a GEDCOM line"""
        source_ids = []
        for subline in self.iterate(line, tag=GedcomTags.SOUR):
            if subline.pointer_value:
                source_ids.append(subline.pointer_value)
        return source_ids
    
    def parse_individual(self, line: GedcomLine) -> Individual:
        if not line.xref_id:
            raise ValueError(f"Individual has no xref_id: {line}")
        
        individual: Individual = Individual(xref_id=line.xref_id, transmission=self)

        for subline in self.iterate(line):
            if subline.tag == GedcomTags.NAME:
                individual.add_name(Name(self).parse(subline))
            elif subline.tag == GedcomTags.BIRT:
                individual.birth_date, individual.birth_place = self.extract_date_place(subline)
            elif subline.tag == GedcomTags.DEAT:
                individual.death_date, individual.death_place = self.extract_date_place(subline)
            elif subline.tag == GedcomTags.FAMS:
                if subline.pointer_value: individual.fams_ids.append(subline.pointer_value)
            elif subline.tag == GedcomTags.FAMC:
                individual.famc_id = subline.pointer_value
            elif subline.tag == GedcomTags.SEX:
                individual.sex = subline.value
            elif subline.tag == GedcomTags.CHR:
                individual.baptism_date, individual.baptism_place = self.extract_date_place(subline)
            elif subline.tag == GedcomTags.BURI:
                individual.burial_date, individual.burial_place = self.extract_date_place(subline)

        return individual
    
    def parse_individuals(self):
        """Parse individuals from the GedcomTransmission"""
        for line in self.iterate(tag=GedcomTags.INDI):
            individual: Individual = self.parse_individual(line)                        
            self.__individual_map[individual.xref_id] = individual

    def parse_family(self, line: GedcomLine) -> Family:
        if not line.xref_id:
            raise ValueError(f"Family has no xref_id: {line}")

        family = Family(xref_id=line.xref_id, transmission=self)

        for subline in self.iterate(line):
            if subline.tag == GedcomTags.HUSB:
                family.husband_id = subline.pointer_value
            elif subline.tag == GedcomTags.WIFE:
                family.wife_id = subline.pointer_value
            elif subline.tag == GedcomTags.CHIL:
                if subline.pointer_value: family.children_ids.append(subline.pointer_value)
            elif subline.tag == GedcomTags.MARR:
                family.marriage = EventDetails(self).parse(subline)
        
        return family

    def parse_families(self):
        """Parse families from the GedcomTransmission"""
        for line in self.iterate(tag=GedcomTags.FAM):
            family = self.parse_family(line)
            self.__family_map[family.xref_id] = family

    def parse_source(self, line: GedcomLine) -> Source:
        if not line.xref_id:
            raise ValueError(f"Source has no xref_id: {line}")

        source = Source(xref_id=line.xref_id, transmission=self)

        for subline in self.iterate(line):
            if subline.tag == GedcomTags.TITL:
                source.title = subline.value
            elif subline.tag == GedcomTags.AUTH:
                source.author = subline.value
            elif subline.tag == GedcomTags.PUBL:
                source.publication = subline.value
            elif subline.tag == GedcomTags.TEXT:
                source.text = subline.value

        return source

    def parse_sources(self):
        """Parse sources from the GedcomTransmission"""
        for line in self.iterate(tag=GedcomTags.SOUR):
            if not line.xref_id:
                continue
            
            source: Source = self.parse_source(line)
            self.__source_map[source.xref_id] = source

    def parse_gedcom(self):
        """Parse the GedcomTransmission and generate all Individual, Family, and Source instances"""
        self.parse_individuals()
        self.parse_families()
        self.parse_sources()

    def get_individual(self, id: str) -> Individual | None:
        return self.__individual_map.get(id, None)
    
    def get_family(self, id: str) -> Family | None:
        return self.__family_map.get(id, None)
    
    def get_source(self, xref_id: str) -> Source | None:
        return self.__source_map.get(xref_id, None)

    @property
    def individuals(self) -> List[Individual]:
        return list(self.__individual_map.values())