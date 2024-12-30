from typing import List
from GedcomLine import GedcomLine

class GedcomTransmission:
    def __init__(self):
        self.all_lines: List[GedcomLine] = []
        self.main_lines: List[GedcomLine] = []
        self.id_map: dict[str, GedcomLine] = {}

    def getSubRecord(self, record: GedcomLine, tag: str) -> GedcomLine:
        for subline in record.sublines:
            if subline.tag == tag:
                while subline.pointer_value:
                    subline =  self.id_map[subline.pointer_value]

                return subline