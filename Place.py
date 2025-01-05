class Place:
    def __init__(self, value: str | None = None):
        self.__value: str | None = value

    @property
    def value(self) -> str | None:
        return self.__value

    @value.setter
    def value(self, value: str | None):
        self.__value = value

    def __str__(self) -> str:
        if not self.__value: return "?"

        parts = [part.strip() for part in self.__value.split(",") if part.strip()]
        return ",".join(parts)
