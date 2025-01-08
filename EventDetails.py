from Place import Place
from Date import Date
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags

class EventDetails:
    def __init__(self):
        self.__date = Date()
        self.__place = Place()
        
    def parse(self, line: GedcomLine) -> 'EventDetails': # type: ignore
        from GedcomTransmission import GedcomTransmission

        """Parse event details from a GEDCOM line"""        
        for subline in GedcomTransmission().iterate(line):
            if subline.tag == GedcomTags.DATE:
                self.date = Date(subline.value)
            elif subline.tag == GedcomTags.PLAC:
                self.place = Place(subline.value)
                
        return self
        
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
