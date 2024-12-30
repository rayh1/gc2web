# FILE: gc2web/GedcomLine.py
class GedcomLine:
    def __init__(self, level, opt_xref_id, tag, value, pointervalue):
        self.level = level
        self.opt_xref_id = opt_xref_id
        self.tag = tag
        self.value = value
        self.pointervalue = pointervalue

    def __repr__(self):
        return f"GedcomLine(level={self.level}, opt_xref_id={self.opt_xref_id}, tag={self.tag}, value={self.value}, pointervalue={self.pointervalue})"