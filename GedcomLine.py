class GedcomLine:
    def __init__(self, level, tag, xref_id, pointer_value, value):
        self.level = level
        self.tag = tag
        self.xref_id = xref_id
        self.pointer_value = pointer_value
        self.value = value

    def __repr__(self):
        return f"GedcomLine(level={self.level}, tag='{self.tag}', xref_id='{self.xref_id}', pointer_value='{self.pointer_value}', value='{self.value}')"
