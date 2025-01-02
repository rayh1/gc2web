class Individual:
    def __init__(self, xref_id: str):
        self.__xref_id = xref_id
        self.__name = "Unknown"
        self.__birth_date = ""
        self.__birth_place = ""
        self.__death_date = ""
        self.__death_place = ""
        self.__fams = []
        self.__famc = None

    @property
    def xref_id(self) -> str:
        return self.__xref_id

    @xref_id.setter
    def xref_id(self, value: str):
        self.__xref_id = value

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
    def fams(self) -> list:
        return self.__fams

    @fams.setter
    def fams(self, value: list):
        self.__fams = value

    @property
    def famc(self) -> str | None:
        return self.__famc

    @famc.setter
    def famc(self, value: str | None):
        self.__famc = value
