class Family:
    def __init__(self, xref_id: str):
        self.xref_id = xref_id
        self.husband = None
        self.wife = None
        self.children = []
        self.marriage_date = ""
        self.marriage_place = ""
