from typing import List

from parser.GedcomLine import GedcomLine
from parser.GedcomTags import GedcomTags
from parser.GedcomParser import GedcomParser

from model.Note import Note

class NotesMixin:
    def __init__(self):
        self.__notes: List[Note] = []

    def parse_notes(self, line: GedcomLine):
        from model.GedcomTransmission import GedcomTransmission

        for subline in GedcomParser().iterate(line, tag=GedcomTags.NOTE):
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
