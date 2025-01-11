from Place import Place
from Date import Date
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags
from SourcesMixin import SourcesMixin

class EventDetails(SourcesMixin):
    def __init__(self):
        super().__init__()

        self.__value: str | None = None

        self.__date = Date()
        self.__place = Place()
        self.__address: str | None = None  # Add address property
        self.__type: str | None = None
        
    def parse(self, line: GedcomLine) -> 'EventDetails': # type: ignore
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
               
        return self
        
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
