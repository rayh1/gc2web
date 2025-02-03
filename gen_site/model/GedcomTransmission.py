from typing import List, Dict
from tqdm import tqdm # type: ignore

from parser.GedcomParser import GedcomParser
from parser.GedcomTags import GedcomTags

from model.Individual import Individual
from model.Family import Family
from model.Source import Source
from model.Repository import Repository

from util.singleton import singleton

@singleton
class GedcomTransmission:
    def __init__(self):
        self.__individual_map: Dict[str, Individual] = {}
        self.__family_map: Dict[str, Family] = {}
        self.__source_map: Dict[str, Source] = {}
        self.__repository_map: Dict[str, Repository] = {}

    def __parse_individuals(self):
        """Parse individuals from the GedcomTransmission"""
        for line in tqdm(list(GedcomParser().iterate(tag=GedcomTags.INDI)), desc="Parsed individuals", bar_format='{desc}: {total_fmt}'):
            individual: Individual = Individual().parse(line)                        
            self.__individual_map[individual.xref_id] = individual

    def __parse_families(self):
        """Parse families from the GedcomTransmission"""
        for line in tqdm(list(GedcomParser().iterate(tag=GedcomTags.FAM)), desc="Parsed families", bar_format='{desc}: {total_fmt}'):
            family = Family().parse(line)
            self.__family_map[family.xref_id] = family

    def __parse_sources(self):
        """Parse sources from the GedcomTransmission"""
        for line in tqdm(list(GedcomParser().iterate(tag=GedcomTags.SOUR)), desc="Parsed sources", bar_format='{desc}: {total_fmt}'):
            if not line.xref_id:
                continue    # Ignore SOUR line in header
            
            source = Source().parse(line)
            self.__source_map[source.xref_id] = source

    def __parse_repositories(self):
        """Parse repositories from the GedcomTransmission"""
        for line in tqdm(list(GedcomParser().iterate(tag=GedcomTags.REPO)), desc="Parsed repositories", bar_format='{desc}: {total_fmt}'):
            repository = Repository().parse(line)
            self.__repository_map[repository.xref_id] = repository

    def __exclude_privates(self):
        """Exclude private individuals from the GedcomTransmission"""
        for individual in tqdm(list(filter(lambda i: i.is_private(), self.individuals)), desc="Excluded private individuals", bar_format='{desc}: {total_fmt}'):
            del self.__individual_map[individual.xref_id]

    def parse_gedcom(self):
        """Parse the GedcomTransmission and generate all Individual, Family, Source, and Repository instances"""
        self.__parse_sources()
        self.__parse_individuals()
        self.__parse_families()
        self.__parse_repositories()

        self.__exclude_privates()

    def get_individual(self, id: str) -> Individual | None:
        return self.__individual_map.get(id, None)
    
    def get_family(self, id: str) -> Family | None:
        return self.__family_map.get(id, None)
    
    def get_source(self, xref_id: str) -> Source | None:
        return self.__source_map.get(xref_id, None)

    def get_repository(self, id: str) -> Repository | None:
        return self.__repository_map.get(id, None)

    @property
    def individuals(self) -> List[Individual]:
        return list(self.__individual_map.values())
    
    @property
    def families(self) -> List[Family]:
        return list(self.__family_map.values())
    
    @property
    def sources(self) -> List[Source]:
        return list(self.__source_map.values())

    @property
    def repositories(self) -> List[Repository]:
        return list(self.__repository_map.values())
    
    def parse_file(self, gedcom_file: str):
        from model.GedcomTransmission import GedcomTransmission
        
        with open(gedcom_file, 'r') as gedcom_stream:
            GedcomParser().parse(gedcom_stream)
            GedcomTransmission().parse_gedcom()

    