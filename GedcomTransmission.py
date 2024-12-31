import re
from typing import List
from GedcomLine import GedcomLine

class GedcomIterator:
    def __init__(self, transmission: 'GedcomTransmission', lines: List[GedcomLine], tag:str | None, value_re: str | None, follow_pointers: bool = True):
        self.transmission: 'GedcomTransmission' = transmission
        self.lines: List[GedcomLine] = lines
        self.tag: str | None = tag
        self.value_re: str | None = value_re
        self.follow_pointers: bool = follow_pointers

        self.cur_index: int = 0

    def __iter__(self):
        return self

    def __next__(self):
        for i, line in enumerate(self.lines[self.cur_index:], start=self.cur_index):
            self.cur_index = i + 1

            if self.tag and self.tag != line.tag:
                continue

            if self.follow_pointers:
                line = self.transmission.follow_pointers(line)

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
            return GedcomIterator(self, self.all_lines, tag, value_re, follow_pointers)
        else:
            return GedcomIterator(self, line.sublines, tag, value_re, follow_pointers)

    def iterate_id(self, id: str, tag: str | None = None, value_re: str | None = None, follow_pointers: bool | None = None) -> GedcomIterator:
            return GedcomIterator(self, self.id_map[id].sublines, tag, value_re, follow_pointers)
    
    def follow_pointers(self, line: GedcomLine) -> GedcomLine:
        while line and line.pointer_value:
            line = self.id_map[line.pointer_value]

        return line
