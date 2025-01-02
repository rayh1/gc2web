class Individual:
    def __init__(self, xref_id: str):
        self.xref_id = xref_id
        self.name = "Unknown"
        self.birth_date = ""
        self.birth_place = ""
        self.death_date = ""
        self.death_place = ""
        self.fams = []
        self.famc = None
