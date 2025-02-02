from GedcomLine import GedcomLine
import yaml # type: ignore

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
    
    def is_yaml(self) -> bool:
        if not self.value:
            return False
        return self.value.strip().startswith('---')
    
    def parse_yaml(self) -> dict | None:
        if not self.is_yaml():
            return None
        try:
            data = yaml.safe_load(self.value) # type: ignore
            return data
        except yaml.YAMLError:
            print(f"Error parsing yaml: {self.value}") 
            return None
    
    def is_private(self) -> bool:
        data = self.parse_yaml()
        if data and 'private' in data:
            return data['private']

        return False

