from Place import Place
from Date import Date
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags
from SourcesMixin import SourcesMixin
from NotesMixin import NotesMixin
from Witness import Witness


class EventDetail(SourcesMixin, NotesMixin):
    def __init__(self):
        super().__init__()
        NotesMixin.__init__(self)

        self.__value: str | None = None

        self.__date = Date()
        self.__place = Place()
        self.__address: str | None = None  # Add address property
        self.__type: str | None = None
        self.__timestamp: str | None = None
        self.__witnesses: list[Witness] = []
        
    def parse(self, line: GedcomLine) -> 'EventDetail': # type: ignore
        from GedcomTransmission import GedcomTransmission

        self.__value = line.value

        for subline in GedcomTransmission().iterate(line):
            if subline.tag == GedcomTags.DATE:
                self.date = Date(subline.value)
            elif subline.tag == GedcomTags.PLAC:
                self.place = Place(subline.value)
            elif subline.tag == GedcomTags.ADDR:
                self.address = subline.value
            elif subline.tag == GedcomTags.TYPE:
                self.type = subline.value

        self.parse_sources(line)
        self.parse_notes(line)
        
        self.parse_timestamp()
        self.parse_witnesses()
               
        return self
    
    def parse_timestamp(self):
        for note in self.notes:
            note_data: dict | None = note.parse_yaml()

            if note_data and 'timestamp' in note_data:
                self.timestamp = note_data['timestamp']
                return

    def parse_witnesses(self):
        for note in self.notes:
            note_data: dict | None = note.parse_yaml()

            if note_data and 'witnesses' in note_data:
                self.__witnesses = [Witness(note.line_num, witness_data) for witness_data in note_data['witnesses']]
                return

    @property
    def value(self) -> str | None:
        return self.__value

    @value.setter
    def value(self, value: str | None):
        self.__value = value
    
    @property
    def date(self) -> Date:
        return self.__date
        
    @date.setter
    def date(self, value: Date):
        self.__date = value
        
    @property
    def place(self) -> Place:
        return self.__place
        
    @place.setter 
    def place(self, value: Place):
        self.__place = value

    @property
    def address(self) -> str | None:
        return self.__address
        
    @address.setter 
    def address(self, value: str | None):
        self.__address = value

    @property
    def type(self) -> str | None:
        return self.__type

    @type.setter
    def type(self, value: str | None):
        self.__type = value

    @property
    def timestamp(self) -> str | None:
        return self.__timestamp

    @timestamp.setter
    def timestamp(self, value: str | None):
        self.__timestamp = value

    @property
    def witnesses(self) -> list[Witness]:
        return self.__witnesses
    
    @property
    def is_defined(self) -> bool:
        return self.date.value is not None
