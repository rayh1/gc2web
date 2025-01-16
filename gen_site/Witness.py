class Witness:
    def __init__(self, data: dict):
        self.__name: str | None = data.get('name', None)
        self.__occupation: str | None = data.get('occupation', None)
        self.__residence: str | None = data.get('residence', None)
        self.__relation: str | None = data.get('relation', None)
        self.__age: int | None = data.get('age', None)
        self.__attribute: str | None = data.get('attribute', None)

    @property
    def name(self) -> str | None:
        return self.__name

    @property
    def occupation(self) -> str | None:
        return self.__occupation

    @property
    def residence(self) -> str | None:
        return self.__residence

    @property
    def relation(self) -> str | None:
        return self.__relation

    @property
    def age(self) -> int | None:
        return self.__age

    @property
    def attribute(self) -> str | None:
        return self.__attribute

    def __repr__(self) -> str:
        return f"Witness(name={self.__name}, occupation={self.__occupation}, residence={self.__residence}, relation={self.__relation}, age={self.__age}, attribute={self.__attribute})"
