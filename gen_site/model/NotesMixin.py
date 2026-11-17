from model.Note import Note


class NotesMixin:
    def __init__(self):
        self.__notes: list[Note] = []

    @property
    def notes(self) -> list[Note]:
        return self.__notes

    @notes.setter
    def notes(self, notes: list[Note]):
        self.__notes = notes

    def add_note(self, note: Note):
        self.__notes.append(note)

    def is_private(self) -> bool:
        return any(note.is_private() for note in self.notes)

    @property
    def plain_notes(self) -> list[Note]:
        # Return a list of all notes that are not yaml
        return [note for note in self.notes if not note.is_yaml()]
