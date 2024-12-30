import re

from typing import List, Optional, TextIO
from collections import deque

from GedcomLine import GedcomLine
from GedcomTags import GedcomTags

class GedcomParser:
    def __init__(self, gedcom_stream: TextIO):
        self.gedcom_stream: TextIO = gedcom_stream
        self.all_lines: List[GedcomLine] = []
        self.main_lines: List[GedcomLine] = []

    def parse_gedcom_line(self, line: str) -> GedcomLine:
        """Parses a single GEDCOM line and returns its components."""
        gedcom_regex = r"^\s*(\d+)\s+(@[^@]+@)?\s*([A-Za-z0-9_]+)\s*(@[^@]+@)?(.+)?$"
        match = re.match(gedcom_regex, line)
        if not match:
            raise ValueError(f"Invalid GEDCOM line: {line}")
        
        level: int = int(match.group(1))
        xref_id: str | None = match.group(2)
        tag: str = match.group(3)
        pointer_value: str | None = match.group(4)
        value: str | None = match.group(5)
        
        return GedcomLine(level, tag, xref_id, pointer_value, value)

    def parse(self):
        """Reads a GEDCOM stream and parses each line into a GedcomLine instance."""
        self.all_lines = []
        self.main_lines = []
        stack: deque[GedcomLine] = deque()
        prev_parsed_line = None

        for line in self.gedcom_stream:
            stripped_line = line.strip()
            if stripped_line:  # Skip empty lines
                try:
                    parsed_line = self.parse_gedcom_line(line)

                    # Parse sublines
                    if (parsed_line.level == 0):
                        stack.clear()
                        self.main_lines.append(parsed_line)
                        stack.append(parsed_line)
                    elif parsed_line.level == stack[-1].level + 1:
                        stack[-1].sublines.append(parsed_line)
                    elif parsed_line.level == stack[-1].level + 2:
                        if prev_parsed_line.tag == GedcomTags.CONC or prev_parsed_line.tag == GedcomTags.CONT:
                            raise ValueError(f"CONT or CONC line cannot have sublines: {parsed_line}")
                        
                        if parsed_line.tag == GedcomTags.CONC:
                            prev_parsed_line.value += parsed_line.value
                            continue

                        if parsed_line.tag == GedcomTags.CONT:
                            prev_parsed_line.value += "\r\n" + parsed_line.value
                            continue

                        stack.append(prev_parsed_line)
                        stack[-1].sublines.append(parsed_line)
                    elif parsed_line.level <= stack[-1].level:
                        while parsed_line.level <= stack[-1].level:
                            stack.pop()
                        stack[-1].sublines.append(parsed_line)
                    else:
                        raise ValueError(f"Invalid level for line: {parsed_line}")
                    
                    self.all_lines.append(parsed_line)
                    prev_parsed_line = parsed_line

                except ValueError as e:
                    print(f"Skipping line due to error: {e}")
