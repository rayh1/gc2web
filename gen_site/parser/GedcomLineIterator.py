from typing import List
import re

from parser.GedcomLine import GedcomLine

class GedcomLineIterator:
    """
    An iterator class for iterating over a list of GedcomLine lines with optional filtering.

    Attributes:
        lines (List[GedcomLine]): The list of GedcomLine lines to iterate over.
        tag (str | None): An optional tag to filter lines by. Only lines with this tag will be returned.
        value_re (str | None): An optional regular expression to filter lines by their value. Only lines with values matching this regex will be returned.
        follow_pointers (bool): A flag indicating whether to follow pointers in the Gedcom lines. Defaults to True.
    Methods:
        __iter__(): Returns the iterator object itself.
        __next__(): Returns the next GedcomLine object that matches the filtering criteria. Raises StopIteration when no more lines are available.
    """
    
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
