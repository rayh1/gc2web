class GedcomLine:
    def __init__(self, level: int, tag: str, xref_id: str | None, pointer_value: str | None, value: str | None):
        self.level: int = level
        self.tag: str = tag
        self.xref_id: str | None = xref_id
        self.pointer_value: str | None = pointer_value
        self.value: str | None = value

    def __repr__(self) -> str:
        return f"GedcomLine(level={self.level}, tag='{self.tag}', xref_id='{self.xref_id}', pointer_value='{self.pointer_value}', value='{self.value}')"
