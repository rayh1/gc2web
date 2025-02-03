from typing import List
import re

from parser.GedcomLine import GedcomLine

class GedcomLineIterator:
    def __init__(self, lines: List[GedcomLine], tag:str | None, value_re: str | None, follow_pointers: bool | None = True):
        self.lines: List[GedcomLine] = lines
        self.tag: str | None = tag
        self.value_re: str | None = value_re
        self.follow_pointers: bool = follow_pointers if follow_pointers != None else False

        self.cur_index: int = 0

    def __iter__(self):
        return self

    def __next__(self):
        from parser.GedcomParser import GedcomParser

        for i, line in enumerate(self.lines[self.cur_index:], start=self.cur_index):
            self.cur_index = i + 1

            if self.tag and self.tag != line.tag:
                continue

            if self.follow_pointers:
                line = GedcomParser().follow_pointers(line)

            if self.value_re != None:
                if line.value == None:
                    continue
                elif re.match(self.value_re, line.value) == None:
                    continue

            return line
                
        raise StopIteration
