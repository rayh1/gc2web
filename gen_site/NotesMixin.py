from typing import List
from Note import Note
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags

class NotesMixin:
    PRIVATE = "PRIVATE"

    def __init__(self):
        self.__notes: List[Note] = []

    def parse_notes(self, line: GedcomLine):
        from GedcomTransmission import GedcomTransmission

        for subline in GedcomTransmission().iterate(line, tag=GedcomTags.NOTE):
            self.add_note(Note().parse(subline))
                
    @property
    def notes(self) -> List[Note]:
        return self.__notes

    def add_note(self, note: Note):
        self.__notes.append(note)

    def is_private(self) -> bool:
        return any(note.value and note.value == self.PRIVATE for note in self.notes)
