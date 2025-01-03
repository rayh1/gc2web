import re
from typing import TextIO
from collections import deque
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags
from GedcomTransmission import GedcomTransmission

class GedcomParser:
    def parse_gedcom_line(self, line: str) -> GedcomLine:
        """Parses a single GEDCOM line and returns its components."""
        gedcom_regex = r"^\s*(\d+)\s+(@[^@]+@)?\s*([A-Za-z0-9_]+)\s*(@[^@]+@)?(.+)?$"
        match = re.match(gedcom_regex, line)
        if not match:
            raise ValueError(f"Invalid GEDCOM line: {line}")
        
        level: int = int(match.group(1))
        xref_id: str | None = match.group(2)[1:-1] if match.group(2) else None
        tag: str = match.group(3)
        pointer_value: str | None = match.group(4)[1:-1] if match.group(4) else None   
        value: str | None = match.group(5)
        
        return GedcomLine(level, tag, xref_id, pointer_value, value)

    def parse(self, gedcom_stream: TextIO) -> GedcomTransmission:
        """Reads a GEDCOM stream and parses each line into a GedcomLine instance."""
        transmission = GedcomTransmission()
        stack: deque[GedcomLine] = deque()
        prev_parsed_line = None
        lineno: int = 0

        for line in gedcom_stream:
            lineno += 1
            stripped_line = line.strip()
            if stripped_line:  # Skip empty lines
                try:
                    parsed_line = self.parse_gedcom_line(line)

                    # Parse sublines
                    if (parsed_line.level == 0):    # Root line
                        stack.clear()
                        transmission.main_lines.append(parsed_line)
                        stack.append(parsed_line)
                    elif parsed_line.level == stack[-1].level + 1: # Subline
                        parsed_line.parent = stack[-1]
                        stack[-1].sublines.append(parsed_line)
                    elif parsed_line.level == stack[-1].level + 2:  # Deeper subline
                        if prev_parsed_line.tag == GedcomTags.CONC or prev_parsed_line.tag == GedcomTags.CONT:
                            raise ValueError(f"CONT or CONC line cannot have sublines: {parsed_line}")
                        
                        if parsed_line.tag == GedcomTags.CONC:
                            value = "" if parsed_line.value == None else parsed_line.value
                            prev_parsed_line.value += parsed_line.value
                            continue

                        if parsed_line.tag == GedcomTags.CONT:
                            value = "" if parsed_line.value == None else parsed_line.value
                            prev_parsed_line.value += "\r\n" + value
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
                    print(f"Skipping line {lineno} due to error: {e}")
                    exit(1)
        
        return transmission
