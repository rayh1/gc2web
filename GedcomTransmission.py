import re
from typing import List
from GedcomLine import GedcomLine

class GedcomIterator:
    def __init__(self, id_map: dict[str, GedcomLine], tag:str | None, value_re: str | None, lines: List[GedcomLine]):
        self.id_map: dict[str, GedcomLine] = id_map
        self.tag: str | None = tag
        self.value_re: str | None = value_re
        self.lines: List[GedcomLine] = lines
        self.index: int = 0

    def __iter__(self):
        return self

    def __next__(self):
        for i, line in enumerate(self.lines[self.index:], start=self.index):
            self.index = i + 1

            if self.tag and self.tag != line.tag:
                continue

            while line and line.pointer_value:
                line = self.id_map[line.pointer_value]

            if self.value_re != None:
                if line.value == None:
                    continue
                elif re.match(self.value_re, line.value) == None:
                    continue

            return line
                
        raise StopIteration

class GedcomTransmission:
    def __init__(self):
        self.all_lines: List[GedcomLine] = []
        self.main_lines: List[GedcomLine] = []
        self.id_map: dict[str, GedcomLine] = {}

    def iterate(self, tag: str | None = None, value_re: str | None = None, line: GedcomLine = None) -> GedcomIterator:
        if line == None:
            return GedcomIterator(self.id_map, tag, value_re, self.all_lines)
        else:
            return GedcomIterator(self.id_map, tag, value_re, line.sublines)

    def getSubRecord(self, record: GedcomLine, tag: str) -> GedcomLine:
        for subline in record.sublines:
            if subline.tag == tag:
                while subline.pointer_value:
                    subline =  self.id_map[subline.pointer_value]

                return subline