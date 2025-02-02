from typing import Union
from Place import Place
from Date import Date
from Name import Name
from EventDetail import EventDetail
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags
from SourcesMixin import SourcesMixin
from datetime import datetime
from NotesMixin import NotesMixin
from Association import Association

class Location:
    """
    Represents an event of an individual itself or together with its spouse.
    """
    def __init__(self, spouse: Union['Individual', None], event: EventDetail): # type: ignore
        self.spouse: Union['Individual', None] = spouse
        self.event: EventDetail = event
class Individual(SourcesMixin, NotesMixin):
    def __init__(self):
        super().__init__()
        NotesMixin.__init__(self)

        self.__xref_id = "xref_id"
        self.__names: list[Name] = []
        self.__birth: EventDetail = EventDetail()
        self.__death: EventDetail = EventDetail()
        self.__baptism: EventDetail = EventDetail()
        self.__burial: EventDetail = EventDetail()
        self.__fams_ids: list[str] = []
        self.__famc_id: str | None = None
        self.__sex: str | None = None
        self.__occupations: list[EventDetail] = []
        self.__residences: list[EventDetail] = []
        self.__facts: list[EventDetail] = []
        self.__associations: list[Association] = []
        self.__descriptions: list[EventDetail] = []

        self.__fams_cache: list['Family'] | None = None # type: ignore
        self.__famc_cache: 'Family' | None = None # type: ignore
        self.__spouses_cache: list['Individual'] | None = None
        self.__locations_cache: list[Location] | None = None

    def parse(self, line: GedcomLine) -> 'Individual':
        from GedcomTransmission import GedcomTransmission

        if not line.xref_id:
            raise ValueError(f"Individual has no xref_id: {line}")        
        self.__xref_id = line.xref_id

        for subline in GedcomTransmission().iterate(line):
            if subline.tag == GedcomTags.NAME:
                self.add_name(Name().parse(subline))
            elif subline.tag == GedcomTags.BIRT:
                self.birth = EventDetail().parse(subline)
            elif subline.tag == GedcomTags.DEAT:
                self.death = EventDetail().parse(subline)
            elif subline.tag == GedcomTags.FAMS:
                if subline.pointer_value: self.fams_ids.append(subline.pointer_value)
            elif subline.tag == GedcomTags.FAMC:
                self.famc_id = subline.pointer_value
            elif subline.tag == GedcomTags.SEX:
                self.sex = subline.value
            elif subline.tag == GedcomTags.CHR:
                self.baptism = EventDetail().parse(subline)
            elif subline.tag == GedcomTags.BURI:
                self.burial = EventDetail().parse(subline)
            elif subline.tag == GedcomTags.OCCU:
                self.add_occupation(EventDetail().parse(subline))
            elif subline.tag == GedcomTags.RESI:
                self.add_residence(EventDetail().parse(subline))
            elif subline.tag == GedcomTags.FACT:
                self.add_fact(EventDetail().parse(subline))
            elif subline.tag == GedcomTags.DSCR:
                self.add_description(EventDetail().parse(subline))

        # Parse associations
        for subline in GedcomTransmission().iterate(line, tag=GedcomTags.ASSO):
            if subline.pointer_value: self.__associations.append(Association().parse(subline))

        self.parse_sources(line)
        self.parse_notes(line)
        
        return self

    @property
    def xref_id(self) -> str:
        return self.__xref_id

    @xref_id.setter
    def xref_id(self, value: str):
        self.__xref_id = value

    @property
    def name(self) -> Name | None:
        return self.__names[0] if len(self.__names) > 0 else None

    @property
    def names(self) -> list[Name]:
        return self.__names

    def add_name(self, value: Name):
        self.__names.append(value)

    @property
    def birth(self) -> EventDetail:
        return self.__birth

    @birth.setter
    def birth(self, value: EventDetail):
        self.__birth = value

    @property
    def death(self) -> EventDetail:
        return self.__death

    @death.setter
    def death(self, value: EventDetail):
        self.__death = value

    @property
    def baptism(self) -> EventDetail:
        return self.__baptism

    @baptism.setter
    def baptism(self, value: EventDetail):
        self.__baptism = value

    @property
    def burial(self) -> EventDetail:
        return self.__burial

    @burial.setter
    def burial(self, value: EventDetail):
        self.__burial = value

    @property
    def fams_ids(self) -> list[str]:
        return self.__fams_ids

    @fams_ids.setter
    def fams_ids(self, value: list[str]):
        self.__fams_ids = value

    @property
    def famc_id(self) -> str | None:
        return self.__famc_id

    @famc_id.setter
    def famc_id(self, value: str | None):
        self.__famc_id = value

    @property
    def sex(self) -> str | None:
        return self.__sex

    @sex.setter
    def sex(self, value: str | None):
        self.__sex = value

    @property
    def occupations(self) -> list[EventDetail]:
        return self.__occupations

    def add_occupation(self, value: EventDetail):
        self.__occupations.append(value)

    @property
    def residences(self) -> list[EventDetail]:
        return self.__residences
    
    def add_residence(self, value: EventDetail):
        self.__residences.append(value)

    @property
    def facts(self) -> list[EventDetail]:
        return self.__facts

    def add_fact(self, value: EventDetail):
        self.__facts.append(value)

    @property
    def descriptions(self) -> list[EventDetail]:
        return self.__descriptions

    def add_description(self, value: EventDetail):
        self.__descriptions.append(value)

    @property
    def associations(self) -> list[Association]:
        return self.__associations

# Utility methods

    @property
    def fams(self) -> list['Family']: # type: ignore
        from GedcomTransmission import GedcomTransmission
        if self.__fams_cache is None:
            self.__fams_cache = list(filter(None, [GedcomTransmission().get_family(fams_id) for fams_id in self.fams_ids]))
        return self.__fams_cache

    @property
    def famc(self) -> 'Family': # type: ignore
        from GedcomTransmission import GedcomTransmission
        if self.__famc_cache is None and self.__famc_id:
            self.__famc_cache = GedcomTransmission().get_family(self.__famc_id)
        return self.__famc_cache # type: ignore

    @property
    def father(self) -> 'Individual':
        if self.famc:
            return self.famc.husband         # type: ignore
        return None # type: ignore

    @property
    def mother(self) -> 'Individual':
        if self.famc:
            return self.famc.wife # type: ignore
        return None # type: ignore

    @property
    def spouses(self) -> list['Individual']:
        if self.__spouses_cache is None:
            self.__spouses_cache = []
            for family in self.fams:
                if (family.husband and family.husband != self):
                    self.__spouses_cache.append(family.husband)
                if (family.wife and family.wife != self):
                    self.__spouses_cache.append(family.wife)
        return self.__spouses_cache

    def children(self, spouse: 'Individual') -> list['Individual']:
        children = []
        for family in self.fams:
            if (family.husband == self and family.wife == spouse) or (family.husband == spouse and family.wife == self):
                children.extend(family.children)
        return children

    @property
    def is_male(self) -> bool:
        return self.__sex == 'M'

    @property
    def is_female(self) -> bool:
        return self.__sex == 'F'

    @property
    def is_unknown_sex(self) -> bool:
        return self.__sex not in ['M', 'F']
    
    @property
    def start_life(self) -> EventDetail:
        return self.birth if self.birth.date.value else self.baptism

    @property
    def end_life(self) -> EventDetail:
        return self.death if self.death.date.value else self.burial

    def age(self, at_date: Date) -> int | None:
        if not self.start_life.date:
            return None
        
        start_life_date_value = self.start_life.date.date()
        at_date_value = at_date.date()
        if not start_life_date_value or not at_date_value:
            return None
        return (at_date_value - start_life_date_value).days // 365
    
    def is_born(self, at_date: Date) -> bool:        
        start_life_date = self.start_life.date.date()
        at_date_value = at_date.date()

        if start_life_date is None or at_date_value is None:
            return False
        
        return start_life_date <= at_date_value

    def locations(self) -> list[Location]:
        if self.__locations_cache is None:
        
            locations: list[Location] = []
                                
            for residence in self.residences:
                locations.append(Location(None, residence))

            for family in self.fams:
                for residence in family.residences:
                    locations.append(Location(family.spouse(self), residence))
                    
            self.__locations_cache = sorted(locations, key=lambda x: x.event.date.date() or datetime.min)

        return self.__locations_cache
    
    def siblings(self) -> list['Individual']:
        if self.famc:
            return sorted(
                    [child for child in self.famc.children if child != self],
                    key=lambda x: x.start_life.date.date() or datetime.max
                )
        return []
    
    def uncles_aunts(self) -> list['Individual']:
        result: list['Individual'] = []
        for parent in [self.father, self.mother]:
            if not parent:
                continue
            for sibling in parent.siblings():
                result.append(sibling)
                for spouse in sibling.spouses:
                    result.append(spouse)

        return result
    
    def has_name(self, name: str) -> bool:
        return any([name == n.plain_value for n in self.names])
    