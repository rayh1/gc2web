from Place import Place
from Date import Date
from Name import Name

class Individual:
    def __init__(self, xref_id: str, transmission: 'GedcomTransmission'): # type: ignore
        self.__xref_id = xref_id
        self.__transmission: 'GedcomTransmission' = transmission # type: ignore
        self.__names: list[Name] = []
        self.__birth_date: Date = Date()
        self.__birth_place: Place = Place()
        self.__death_date: Date = Date()
        self.__death_place: Place = Place()
        self.__fams_ids: list[str] = []
        self.__famc_id: str | None = None
        self.__sex: str | None = None
        self.__baptism_date: Date = Date()
        self.__baptism_place: Place = Place()
        self.__burial_date: Date = Date()
        self.__burial_place: Place = Place()
        self.__fams_cache: list['Family'] | None = None # type: ignore
        self.__famc_cache: 'Family' | None = None # type: ignore
        self.__spouses_cache: list['Individual'] | None = None

    @property
    def xref_id(self) -> str:
        return self.__xref_id

    @xref_id.setter
    def xref_id(self, value: str):
        self.__xref_id = value

    @property
    def transmission(self) -> 'GedcomTransmission': # type: ignore
        return self.__transmission

    @transmission.setter
    def transmission(self, value: 'GedcomTransmission'): # type: ignore
        self.__transmission = value

    @property
    def name(self) -> Name | None:
        return self.__names[0] if len(self.__names) > 0 else None

    @property
    def names(self) -> list[Name]:
        return self.__names

    def add_name(self, value: Name):
        self.__names.append(value)

    @property
    def birth_date(self) -> Date:
        return self.__birth_date

    @birth_date.setter
    def birth_date(self, value: Date):
        self.__birth_date = value

    @property
    def birth_place(self) -> Place:
        return self.__birth_place

    @birth_place.setter
    def birth_place(self, value: Place):
        self.__birth_place = value

    @property
    def death_date(self) -> Date:
        return self.__death_date

    @death_date.setter
    def death_date(self, value: Date):
        self.__death_date = value

    @property
    def death_place(self) -> Place:
        return self.__death_place

    @death_place.setter
    def death_place(self, value: Place):
        self.__death_place = value

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
    def baptism_date(self) -> Date:
        return self.__baptism_date

    @baptism_date.setter
    def baptism_date(self, value: Date):
        self.__baptism_date = value

    @property
    def baptism_place(self) -> Place:
        return self.__baptism_place

    @baptism_place.setter
    def baptism_place(self, value: Place):
        self.__baptism_place = value

    @property
    def burial_date(self) -> Date:
        return self.__burial_date

    @burial_date.setter
    def burial_date(self, value: Date):
        self.__burial_date = value

    @property
    def burial_place(self) -> Place:
        return self.__burial_place

    @burial_place.setter
    def burial_place(self, value: Place):
        self.__burial_place = value

# Utility methods

    @property
    def fams(self) -> list['Family']: # type: ignore
        if self.__fams_cache is None:
            self.__fams_cache = [self.transmission.get_family(fams_id) for fams_id in self.fams_ids]
        return self.__fams_cache

    @property
    def famc(self) -> 'Family': # type: ignore
        if self.__famc_cache is None:
            self.__famc_cache = self.__transmission.get_family(self.__famc_id)
        return self.__famc_cache

    @property
    def father(self) -> 'Individual':
        if self.famc:
            return self.famc.husband
        return None # type: ignore

    @property
    def mother(self) -> 'Individual':
        if self.famc:
            return self.famc.wife
        return None # type: ignore

    @property
    def spouses(self) -> list['Individual']:
        if self.__spouses_cache is None:
            self.__spouses_cache = []
            for family in self.fams:
                if family.husband and family.husband != self:
                    self.__spouses_cache.append(family.husband)
                if family.wife and family.wife != self:
                    self.__spouses_cache.append(family.wife)
        return self.__spouses_cache

    @property # type: ignore
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
