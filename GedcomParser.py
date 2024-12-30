import re

from GedcomLine import GedcomLine
from typing import List, Optional, TextIO
from collections import deque

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
        value: str | None = match.group(5).strip() if match.group(5) else None
        
        return GedcomLine(level, tag, xref_id, pointer_value, value)

    def parse(self):
        """Reads a GEDCOM stream and parses each line into a GedcomLine instance."""
        self.all_lines = []
        self.main_lines = []
        stack: deque[GedcomLine] = deque()
        prev_parsed_line = None

        for line in self.gedcom_stream:
            line = line.strip()
            if line:  # Skip empty lines
                try:
                    parsed_line = self.parse_gedcom_line(line)
                    self.all_lines.append(parsed_line)

                    if (parsed_line.level == 0):
                        stack.clear()
                        self.main_lines.append(parsed_line)
                        stack.append(parsed_line)
                    elif prev_parsed_line.level == parsed_line.level:
                        stack[-1].sublines.append(parsed_line)
                    elif prev_parsed_line.level < parsed_line.level:
                        stack.append(prev_parsed_line)
                        stack[-1].sublines.append(parsed_line)
                    else: # stack[-1].level > parsed_line.level
                        while stack[-1].level >= parsed_line.level:
                            stack.pop()
                        stack[-1].sublines.append(parsed_line)

                    prev_parsed_line = parsed_line

                except ValueError as e:
                    print(f"Skipping line due to error: {e}")
