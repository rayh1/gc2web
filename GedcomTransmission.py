import re
from typing import List
from GedcomLine import GedcomLine

class GedcomIterator:
    def __init__(self, id_map: dict[str, GedcomLine], lines: List[GedcomLine], tag:str | None, value_re: str | None, follow_pointers: bool = True):
        self.id_map: dict[str, GedcomLine] = id_map
        self.lines: List[GedcomLine] = lines
        self.tag: str | None = tag
        self.value_re: str | None = value_re
        self.follow_pointers: bool = follow_pointers
        self.index: int = 0

    def __iter__(self):
        return self

    def __next__(self):
        for i, line in enumerate(self.lines[self.index:], start=self.index):
            self.index = i + 1

            if self.tag and self.tag != line.tag:
                continue

            if self.follow_pointers:
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

    def iterate(self, line: GedcomLine = None, tag: str | None = None, value_re: str | None = None, follow_pointers: bool | None = None) -> GedcomIterator:
        if line == None:
            return GedcomIterator(self.id_map, self.all_lines, tag, value_re, follow_pointers)
        else:
            return GedcomIterator(self.id_map, line.sublines, tag, value_re, follow_pointers)

    def iterate_id(self, id: str, tag: str | None = None, value_re: str | None = None, follow_pointers: bool | None = None) -> GedcomIterator:
            return GedcomIterator(self.id_map, self.id_map[id].sublines, tag, value_re, follow_pointers)
