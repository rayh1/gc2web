from parser.GedcomParser import GedcomParser
from parser.GedcomLine import GedcomLine
from parser.GedcomTags import GedcomTags

from model.SourcesMixin import SourcesMixin
from model.NotesMixin import NotesMixin
from model.Individual import Individual
from model.EventDetail import EventDetail

class Family(SourcesMixin, NotesMixin):
    def __init__(self):
        super().__init__()
        NotesMixin.__init__(self)

        self.__xref_id: str = ""
        self.__husband_id: str | None = None
        self.__wife_id: str | None = None
        self.__children_ids: list[str] = []
        self.__marriage: EventDetail = EventDetail()
        self.__residences: list[EventDetail] = []
        
        self.__husband_cache: Individual | None = None
        self.__wife_cache: Individual | None = None
        self.__children_cache: list[Individual] | None = None

    def parse(self, line: GedcomLine) -> 'Family':
        """Parse a family from a GEDCOM line"""
        from model.GedcomTransmission import GedcomTransmission

        if not line.xref_id:
            raise ValueError(f"Family has no xref_id: {line}")
        self.__xref_id: str = line.xref_id
        
        for subline in GedcomParser().iterate(line):
            if subline.tag == GedcomTags.HUSB:
                self.husband_id = subline.pointer_value
            elif subline.tag == GedcomTags.WIFE:
                self.wife_id = subline.pointer_value
            elif subline.tag == GedcomTags.CHIL:
                if subline.pointer_value: self.children_ids.append(subline.pointer_value)
            elif subline.tag == GedcomTags.MARR:
                self.marriage = EventDetail().parse(subline)
            elif subline.tag == GedcomTags.RESI:
                self.residences.append(EventDetail().parse(subline))
        
        self.parse_sources(line)
        self.parse_notes(line)
        
        return self
    
# Properties

    @property
    def xref_id(self) -> str:
        return self.__xref_id

    @xref_id.setter
    def xref_id(self, value: str):
        self.__xref_id = value

    @property
    def husband_id(self) -> str | None:
        return self.__husband_id

    @husband_id.setter
    def husband_id(self, value: str | None):
        self.__husband_id = value

    @property
    def wife_id(self) -> str | None:
        return self.__wife_id

    @wife_id.setter
    def wife_id(self, value: str | None):
        self.__wife_id = value

    @property
    def children_ids(self) -> list[str]:
        return self.__children_ids

    @children_ids.setter
    def children_ids(self, value: list[str]):
        self.__children_ids = value

    @property
    def marriage(self) -> EventDetail:
        return self.__marriage

    @marriage.setter
    def marriage(self, value: EventDetail):
        self.__marriage = value

    @property
    def residences(self) -> list[EventDetail]:
        return self.__residences

    @residences.setter
    def residences(self, value: list[EventDetail]):
        self.__residences = value

# Utility

    @property
    def husband(self) -> Individual | None:
        from model.GedcomTransmission import GedcomTransmission
        if self.__husband_cache is None and self.husband_id:
            self.__husband_cache = GedcomTransmission().get_individual(self.husband_id)
        return self.__husband_cache

    @property
    def wife(self) -> Individual | None:
        from model.GedcomTransmission import GedcomTransmission
        if self.__wife_cache is None and self.wife_id:
            self.__wife_cache = GedcomTransmission().get_individual(self.wife_id)
        return self.__wife_cache
    
    @property
    def children(self) -> list[Individual]:
        from model.GedcomTransmission import GedcomTransmission
        if self.__children_cache is None:
            self.__children_cache = list(filter(None, (GedcomTransmission().get_individual(child_id) for child_id in self.children_ids)))
        return self.__children_cache

    def spouse(self, individual: Individual) -> Individual | None:
        if individual.xref_id == self.husband_id:
            return self.wife
        elif individual.xref_id == self.wife_id:
            return self.husband
        else:
            return None
