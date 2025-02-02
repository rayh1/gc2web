from NotesMixin import NotesMixin
from singleton import singleton

@singleton
class Footnote:
    def __init__(self):
        self.__notes: list[str] = []

    def reset(self):
        self.__notes = []

    @property
    def num(self) -> int:
        return len(self.__notes)
    
    def add(self, notes: NotesMixin | None) -> str:
        result = ""
        if not notes:
            return result
        
        counter: int = len(self.__notes) + 1
        for note in notes.plain_notes:
            result += f"[^{counter}] "
            self.__notes.append(note.value) # type: ignore
            counter += 1

        return result
    
    def gen(self, content: list[str]):
        for count in range(len(self.__notes)):
            content.append(f"[^{count + 1}]: {self.__notes[count]}")
        self.reset()
