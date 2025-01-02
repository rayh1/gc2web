class GedcomLine:
    def __init__(self, level: int, tag: str, xref_id: str | None, pointer_value: str | None, value: str | None):
        self.__level: int = level
        self.__tag: str = tag
        self.__xref_id: str | None = xref_id
        self.__pointer_value: str | None = pointer_value
        self.__value: str | None = value
        self.__sublines: list[GedcomLine] = []
        self.__parent: GedcomLine | None = None

    @property
    def level(self) -> int:
        return self.__level

    @level.setter 
    def level(self, value: int):
        self.__level = value

    @property
    def tag(self) -> str:
        return self.__tag

    @tag.setter
    def tag(self, value: str):
        self.__tag = value

    @property
    def xref_id(self) -> str | None:
        return self.__xref_id

    @xref_id.setter
    def xref_id(self, value: str | None):
        self.__xref_id = value

    @property
    def pointer_value(self) -> str | None:
        return self.__pointer_value

    @pointer_value.setter
    def pointer_value(self, value: str | None):
        self.__pointer_value = value

    @property
    def value(self) -> str | None:
        return self.__value

    @value.setter
    def value(self, value: str | None):
        self.__value = value

    @property
    def sublines(self) -> list["GedcomLine"]:
        return self.__sublines

    @sublines.setter
    def sublines(self, value: list["GedcomLine"]):
        self.__sublines = value

    @property
    def parent(self) -> "GedcomLine | None":
        return self.__parent

    @parent.setter
    def parent(self, value: "GedcomLine | None"):
        self.__parent = value

    def __repr__(self) -> str:
        return f"[level={self.level}, tag='{self.tag}', xref_id='{self.xref_id}', pointer_value='{self.pointer_value}', value='{self.value}']"

    def print(self, parent_tag: str = "", indent: int = 0):
        print("  " * indent, end="")
        print(f"<{parent_tag}> {str(self)}")
        for subline in self.sublines:
            subline.print(self.tag, indent=indent + 1)
