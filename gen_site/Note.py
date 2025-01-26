from GedcomLine import GedcomLine
import yaml

class Note:
    def __init__(self):
        self.__line_num: int | None = None
        self.__value: str | None = None

    def parse(self, line: GedcomLine) -> 'Note':

        self.__line_num = line.line_num
        self.__value = line.value

        return self

    @property
    def value(self) -> str | None:
        return self.__value

    @value.setter
    def value(self, value: str | None):
        self.__value = value

    @property
    def line_num(self) -> int | None:
        return self.__line_num

    @line_num.setter
    def line_num(self, value: int | None):
        self.__line_num = value

    def __repr__(self) -> str:
        return f"Note(xref_id=text={self.value}, line_num={self.__line_num})"
    
    def is_private(self) -> bool:
        if not self.value:
            return False
        
        try:
            note_data = yaml.safe_load(self.value)
            if type(note_data) is dict and 'private' in note_data:
                return note_data['private']
        except yaml.YAMLError:
            pass
        
        return False

