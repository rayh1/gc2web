class Family:
    def __init__(self, xref_id: str):
        self.__xref_id: str = xref_id
        self.__husband: str | None = None
        self.__wife: str | None = None
        self.__children: list[str] = []
        self.__marriage_date: str = None
        self.__marriage_place: str = None

    @property
    def xref_id(self) -> str:
        return self.__xref_id

    @xref_id.setter
    def xref_id(self, value: str):
        self.__xref_id = value

    @property
    def husband(self) -> str | None:
        return self.__husband

    @husband.setter
    def husband(self, value: str | None):
        self.__husband = value

    @property
    def wife(self) -> str | None:
        return self.__wife

    @wife.setter
    def wife(self, value: str | None):
        self.__wife = value

    @property
    def children(self) -> list[str]:
        return self.__children

    @children.setter
    def children(self, value: list[str]):
        self.__children = value

    @property
    def marriage_date(self) -> str:
        return self.__marriage_date

    @marriage_date.setter
    def marriage_date(self, value: str):
        self.__marriage_date = value

    @property
    def marriage_place(self) -> str:
        return self.__marriage_place

    @marriage_place.setter
    def marriage_place(self, value: str):
        self.__marriage_place = value
