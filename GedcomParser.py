from GedcomLine import GedcomLine
import re

class GedcomParser:
    def __init__(self, gedcom_stream):
        self.gedcom_stream = gedcom_stream
        self.lines = []

    def parse_gedcom_line(self, line):
        """Parses a single GEDCOM line and returns its components."""
        gedcom_regex = r"^\s*(\d+)\s+(@[^@]+@)?\s*([A-Za-z0-9_]+)\s*(@[^@]+@)?(.+)?$"
        match = re.match(gedcom_regex, line)
        if not match:
            raise ValueError(f"Invalid GEDCOM line: {line}")
        level = int(match.group(1))
        xref_id = match.group(2)
        tag = match.group(3)
        pointer_value = match.group(4)
        value = match.group(5).strip() if match.group(5) else None
        return GedcomLine(level, tag, xref_id, pointer_value, value)

    def parse(self):
        """Reads a GEDCOM stream and parses each line into a GedcomLine instance."""
        self.lines = []
        for line in self.gedcom_stream:
            line = line.strip()
            if line:  # Skip empty lines
                try:
                    parsed_line = self.parse_gedcom_line(line)
                    self.lines.append(parsed_line)
                except ValueError as e:
                    print(f"Skipping line due to error: {e}")
        return self.lines
