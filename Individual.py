class Individual:
    def __init__(self, xref_id: str, transmission: 'GedcomTransmission'): # type: ignore
        self.__xref_id = xref_id
        self.__transmission: 'GedcomTransmission' = transmission # type: ignore
        self.__name = "Unknown"
        self.__birth_date = None
        self.__birth_place = None
        self.__death_date = None
        self.__death_place = None
        self.__fams_ids = []
        self.__famc_id = None
        self.__sex = None  # Initialize the sex property
        self.__baptism_date = None
        self.__baptism_place = None
        self.__burial_date = None
        self.__burial_place = None

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
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value

    @property
    def birth_date(self) -> str:
        return self.__birth_date

    @birth_date.setter
    def birth_date(self, value: str):
        self.__birth_date = value

    @property
    def birth_place(self) -> str:
        return self.__birth_place

    @birth_place.setter
    def birth_place(self, value: str):
        self.__birth_place = value

    @property
    def death_date(self) -> str:
        return self.__death_date

    @death_date.setter
    def death_date(self, value: str):
        self.__death_date = value

    @property
    def death_place(self) -> str:
        return self.__death_place

    @death_place.setter
    def death_place(self, value: str):
        self.__death_place = value

    @property
    def fams_ids(self) -> list:
        return self.__fams_ids

    @fams_ids.setter
    def fams_ids(self, value: list):
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
    def baptism_date(self) -> str:
        return self.__baptism_date

    @baptism_date.setter
    def baptism_date(self, value: str):
        self.__baptism_date = value

    @property
    def baptism_place(self) -> str:
        return self.__baptism_place

    @baptism_place.setter
    def baptism_place(self, value: str):
        self.__baptism_place = value

    @property
    def burial_date(self) -> str:
        return self.__burial_date

    @burial_date.setter
    def burial_date(self, value: str):
        self.__burial_date = value

    @property
    def burial_place(self) -> str:
        return self.__burial_place

    @burial_place.setter
    def burial_place(self, value: str):
        self.__burial_place = value

# Utility methods

    @property
    def fams(self) -> list['Family']: # type: ignore
        return [self.transmission.get_family(fams_id) for fams_id in self.fams_ids]

    @property
    def famc(self) -> 'Family': # type: ignore
        return self.__transmission.get_family(self.__famc_id)

    @property
    def father(self) -> 'Individual':
        if self.famc:
            return self.famc.husband
        return None

    @property
    def mother(self) -> 'Individual':
        if self.famc:
            return self.famc.wife
        return None

    @property
    def spouses(self) -> list['Individual']:
        spouses = []
        for family in self.fams:
            if family.husband and family.husband != self:
                spouses.append(family.husband)
            if family.wife and family.wife != self:
                spouses.append(family.wife)
        return spouses

    @property
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
