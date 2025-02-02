from typing import List
from Note import Note
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags

class NotesMixin:
    def __init__(self):
        self.__notes: List[Note] = []

    def parse_notes(self, line: GedcomLine):
        from GedcomTransmission import GedcomTransmission

        for subline in GedcomTransmission().iterate(line, tag=GedcomTags.NOTE):
            self.add_note(Note().parse(subline))
                
    @property
    def notes(self) -> List[Note]:
        return self.__notes
    
    @notes.setter
    def notes(self, notes: List[Note]):
        self.__notes = notes

    def add_note(self, note: Note):
        self.__notes.append(note)

    def is_private(self) -> bool:
        return any(note.is_private() for note in self.notes)
    
    @property
    def plain_notes(self) -> List[Note]:
        # Return a list of all notes that are not yaml
        return [note for note in self.notes if not note.is_yaml()]
