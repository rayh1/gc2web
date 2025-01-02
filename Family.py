class Family:
    def __init__(self, xref_id: str):
        self.__xref_id = xref_id
        self.__husband = None
        self.__wife = None
        self.__children = []
        self.__marriage_date = ""
        self.__marriage_place = ""

    @property
    def xref_id(self):
        return self.__xref_id

    @xref_id.setter
    def xref_id(self, value):
        self.__xref_id = value

    @property
    def husband(self):
        return self.__husband

    @husband.setter
    def husband(self, value):
        self.__husband = value

    @property
    def wife(self):
        return self.__wife

    @wife.setter
    def wife(self, value):
        self.__wife = value

    @property
    def children(self):
        return self.__children

    @children.setter
    def children(self, value):
        self.__children = value

    @property
    def marriage_date(self):
        return self.__marriage_date

    @marriage_date.setter
    def marriage_date(self, value):
        self.__marriage_date = value

    @property
    def marriage_place(self):
        return self.__marriage_place

    @marriage_place.setter
    def marriage_place(self, value):
        self.__marriage_place = value
