from Individual import Individual
from Place import Place

class Family:
    def __init__(self, xref_id: str, transmission: 'GedcomTransmission'): # type: ignore
        self.__xref_id: str = xref_id
        self.__transmission: 'GedcomTransmission' = transmission # type: ignore
        self.__husband_id: str | None = None
        self.__wife_id: str | None = None
        self.__children_ids: list[str] = []
        self.__marriage_date: str | None = None
        self.__marriage_place: Place = Place()
        self.__husband_cache: Individual | None = None
        self.__wife_cache: Individual | None = None
        self.__children_cache: list[Individual] | None = None

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
    def marriage_date(self) -> str | None:
        return self.__marriage_date

    @marriage_date.setter
    def marriage_date(self, value: str | None):
        self.__marriage_date = value

    @property
    def marriage_place(self) -> Place:
        return self.__marriage_place

    @marriage_place.setter
    def marriage_place(self, value: Place):
        self.__marriage_place = value

# Utility methods

    @property
    def husband(self) -> Individual | None:
        if self.__husband_cache is None:
            self.__husband_cache = self.transmission.get_individual(self.husband_id)
        return self.__husband_cache

    @property
    def wife(self) -> Individual | None:
        if self.__wife_cache is None:
            self.__wife_cache = self.transmission.get_individual(self.wife_id)
        return self.__wife_cache
    
    @property
    def children(self) -> list[Individual]:
        if self.__children_cache is None:
            self.__children_cache = [self.transmission.get_individual(child_id) for child_id in self.children_ids]
        return self.__children_cache

    def spouse(self, individual: Individual) -> Individual | None:
        if individual.xref_id == self.husband_id:
            return self.wife
        elif individual.xref_id == self.wife_id:
            return self.husband
        else:
            return None
