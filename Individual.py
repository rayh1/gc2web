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
    def fams(self) -> list['Family']: # type: ignore
        return [self.transmission.get_family(fams_id) for fams_id in self.fams_ids]

    @property
    def famc(self) -> 'Family': # type: ignore
        return self.__transmission.get_family(self.__famc_id)
