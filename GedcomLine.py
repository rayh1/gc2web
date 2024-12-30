class GedcomLine:
    def __init__(self, level: int, tag: str, xref_id: str | None, pointer_value: str | None, value: str | None):
        self.level: int = level
        self.tag: str = tag
        self.xref_id: str | None = xref_id
        self.pointer_value: str | None = pointer_value
        self.value: str | None = value
        self.sublines: list[GedcomLine] = []

    def __repr__(self) -> str:
        return f"[level={self.level}, tag='{self.tag}', xref_id='{self.xref_id}', pointer_value='{self.pointer_value}', value='{self.value}']"

    def print(self, parent_tag: str = "", indent: int = 0):
        print("  " * indent, end="")
        print(f"<{parent_tag}> {str(self)}")
        for subline in self.sublines:
            subline.print(self.tag, indent=indent + 1)
