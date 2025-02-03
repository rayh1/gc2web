import re
from typing import Dict, List, TextIO
from collections import deque

from tqdm import tqdm # type: ignore
from util.singleton import singleton

from parser.GedcomLineIterator import GedcomLineIterator
from parser.GedcomLine import GedcomLine
from parser.GedcomTags import GedcomTags

@singleton
class GedcomParser:
    GEDCOM_REGEX = r"^\s*(\d+)\s+(@[^@]+@)?\s*([A-Za-z0-9_]+)\s?(@[^@]+@)?(.+)?$"
    CONT_SEP: str = "\r\n"

    def __init__(self):
        self.__all_lines: List[GedcomLine] = []
        self.__main_lines: List[GedcomLine] = []        
        self.__id_map: dict[str, GedcomLine] = {}

    @property
    def all_lines(self) -> List[GedcomLine]:
        return self.__all_lines

    @property
    def main_lines(self) -> List[GedcomLine]:
        return self.__main_lines
    
    @property
    def id_map(self) -> Dict[str, GedcomLine]:
        return self.__id_map

    def __add_str(self, s1: str | None, s2: str | None, sep: str = "") -> str:
        if s1 and s2:
            return s1 + sep + s2
        elif s1:
            return s1 + sep
        elif s2:
            return sep + s2
        else:
            return sep

    def __parse_gedcom_line(self, line_num: int, line: str) -> GedcomLine:
        match = re.match(self.GEDCOM_REGEX, line)
        if not match:
            raise ValueError(f"Invalid GEDCOM line: {line}")
        
        level: int = int(match.group(1))
        xref_id: str | None = match.group(2)[1:-1] if match.group(2) else None
        tag: str = match.group(3)
        pointer_value: str | None = match.group(4)[1:-1] if match.group(4) else None   
        value: str | None = match.group(5)
        
        return GedcomLine(line_num, level, tag, xref_id, pointer_value, value)

    def parse(self, gedcom_stream: TextIO):
        stack: deque[GedcomLine] = deque()
        prev_parsed_line: GedcomLine | None = None
        line_num: int = 0

        for line in tqdm(list(gedcom_stream), desc="Parsed file lines", bar_format='{desc}: {total_fmt}'):
            line_num += 1
            stripped_line = line.strip()
            if stripped_line:  # Skip empty lines
                try:
                    parsed_line = self.__parse_gedcom_line(line_num, line)

                    # Parse sublines
                    if (parsed_line.level == 0):    # Root line
                        stack.clear()
                        self.main_lines.append(parsed_line)
                        stack.append(parsed_line)
                    elif parsed_line.level == stack[-1].level + 1: # Subline
                        parsed_line.parent = stack[-1]
                        stack[-1].sublines.append(parsed_line)
                    elif parsed_line.level == stack[-1].level + 2:  # Deeper subline
                        if not prev_parsed_line:
                            raise ValueError(f"Level increase without previous line: {parsed_line}")
                        
                        if prev_parsed_line.tag == GedcomTags.CONC or prev_parsed_line.tag == GedcomTags.CONT:
                            raise ValueError(f"CONT or CONC line cannot have sublines: {parsed_line}")
                        
                        if parsed_line.tag == GedcomTags.CONC:
                            prev_parsed_line.value = self.__add_str(prev_parsed_line.value, parsed_line.value)
                            continue

                        if parsed_line.tag == GedcomTags.CONT:
                            prev_parsed_line.value = self.__add_str(prev_parsed_line.value, parsed_line.value, self.CONT_SEP)
                            continue

                        stack.append(prev_parsed_line)
                        parsed_line.parent = stack[-1]
                        stack[-1].sublines.append(parsed_line)
                    elif parsed_line.level <= stack[-1].level:  # Higher level subline
                        while parsed_line.level <= stack[-1].level:
                            stack.pop()
                        parsed_line.parent = stack[-1]
                        stack[-1].sublines.append(parsed_line)
                    else:
                        raise ValueError(f"Invalid level for line: {parsed_line}")

                    # Store xref_id mappings
                    if parsed_line.xref_id:
                        self.id_map[parsed_line.xref_id] = parsed_line
                    
                    # Bookkeeping
                    self.all_lines.append(parsed_line)
                    prev_parsed_line = parsed_line

                except (ValueError, TypeError, AttributeError) as e:
                    print(f"Skipping line {line} due to error: {e}")
                    exit(1)
            
    def iterate(self, line: GedcomLine | None = None, tag: str | None = None, value_re: str | None = None, follow_pointers: bool | None = None) -> GedcomLineIterator:
        """
        Iterate over Gedcom lines based on specified criteria.

        Args:
            line (GedcomLine, optional): Iterate over all sublines of this line. If None, iterate over all lines.
            tag (str, optional): The tag to filter lines by. If None, no tag filtering is applied.
            value_re (str, optional): A regular expression to filter lines by their value. If None, no value filtering is applied.
            follow_pointers (bool, optional): If True, follow pointers during iteration. If None, pointers are not followed.

        Returns:
            GedcomIterator: An iterator over the filtered Gedcom lines.
        """
        if line == None:
            return GedcomLineIterator(self.main_lines, tag, value_re, follow_pointers)
        else:
            return GedcomLineIterator(line.sublines, tag, value_re, follow_pointers)

    def iterate_id(self, id: str, tag: str | None = None, value_re: str | None = None, follow_pointers: bool | None = None) -> GedcomLineIterator:
        """
        Iterate over Gedcom lines based on specified criteria.

        Args:
            id (GedcomLine, optional): Find a line with this id and iterate over all its sublines.
            tag (str, optional): The tag to filter lines by. If None, no tag filtering is applied.
            value_re (str, optional): A regular expression to filter lines by their value. If None, no value filtering is applied.
            follow_pointers (bool, optional): If True, follow pointers during iteration. If None, pointers are not followed.

        Returns:
            GedcomIterator: An iterator over the filtered Gedcom lines.
        """
        return GedcomLineIterator(self.id_map[id].sublines, tag, value_re, follow_pointers)
        
    def follow_pointers(self, line: GedcomLine) -> GedcomLine:
        while line and line.pointer_value:
            line = self.id_map[line.pointer_value]

        return line



