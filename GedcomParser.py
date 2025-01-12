import re
from typing import TextIO
from collections import deque

from tqdm import tqdm
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags
from GedcomTransmission import GedcomTransmission

class GedcomParser:
    GEDCOM_REGEX = r"^\s*(\d+)\s+(@[^@]+@)?\s*([A-Za-z0-9_]+)\s*(@[^@]+@)?(.+)?$"
    CONT_SEP: str = "\r\n"

    def add_str(self, s1: str | None, s2: str | None, sep: str = "") -> str:
        """Concatenates two strings with an optional separator, ignoring None values."""
        if s1 and s2:
            return s1 + sep + s2
        elif s1:
            return s1 + sep
        elif s2:
            return sep + s2
        else:
            return sep

    def parse_gedcom_line(self, line_num: int, line: str) -> GedcomLine:
        """Parses a single GEDCOM line and returns its components."""
        match = re.match(self.GEDCOM_REGEX, line)
        if not match:
            raise ValueError(f"Invalid GEDCOM line: {line}")
        
        level: int = int(match.group(1))
        xref_id: str | None = match.group(2)[1:-1] if match.group(2) else None
        tag: str = match.group(3)
        pointer_value: str | None = match.group(4)[1:-1] if match.group(4) else None   
        value: str | None = match.group(5)
        
        return GedcomLine(line_num, level, tag, xref_id, pointer_value, value)

    def parse(self, gedcom_stream: TextIO) -> GedcomTransmission:
        """Reads a GEDCOM stream and parses each line into a GedcomLine instance."""
        transmission: GedcomTransmission = GedcomTransmission()
        stack: deque[GedcomLine] = deque()
        prev_parsed_line: GedcomLine | None = None
        line_num: int = 0

        for line in tqdm(list(gedcom_stream), desc="Parsing file lines"):
            line_num += 1
            stripped_line = line.strip()
            if stripped_line:  # Skip empty lines
                try:
                    parsed_line = self.parse_gedcom_line(line_num, line)

                    # Parse sublines
                    if (parsed_line.level == 0):    # Root line
                        stack.clear()
                        transmission.main_lines.append(parsed_line)
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
                            prev_parsed_line.value = self.add_str(prev_parsed_line.value, parsed_line.value)
                            continue

                        if parsed_line.tag == GedcomTags.CONT:
                            prev_parsed_line.value = self.add_str(prev_parsed_line.value, parsed_line.value, self.CONT_SEP)
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
                        transmission.id_map[parsed_line.xref_id] = parsed_line
                    
                    # Bookkeeping
                    transmission.all_lines.append(parsed_line)
                    prev_parsed_line = parsed_line

                except (ValueError, TypeError, AttributeError) as e:
                    print(f"Skipping line {line} due to error: {e}")
                    exit(1)
        
        return transmission
