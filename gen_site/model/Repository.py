class Repository:
    def __init__(self):
        self.__xref_id: str = ""
        self.__name: str | None = None
        self.__www: str | None = None

    @property
    def xref_id(self) -> str:
        return self.__xref_id

    @xref_id.setter
    def xref_id(self, value: str):
        self.__xref_id = value

    @property
    def name(self) -> str | None:
        return self.__name

    @name.setter
    def name(self, value: str | None):
        self.__name = value

    @property
    def www(self) -> str | None:
        return self.__www

    @www.setter
    def www(self, value: str | None):
        self.__www = value

    def __repr__(self) -> str:
        return f"Repository(xref_id={self.xref_id}, name={self.name})"
