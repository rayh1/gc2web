class Name:
    def __init__(self, value: str | None = None):
        self.__value: str | None = value

    @property
    def value(self) -> str | None:
        return self.__value

    @value.setter
    def value(self, value: str | None):
        self.__value = value

    def __str__(self) -> str:
        return self.__value.replace("/", "") if self.__value else "?"
