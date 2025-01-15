import unittest
import yaml
from EventDetail import EventDetail, Witness
from Note import Note

class TestEventDetail(unittest.TestCase):
    def setUp(self):
        self.event_detail = EventDetail()

    def test_parse_witnesses_with_valid_data(self):
        note_value = """
---
witnesses:
  - name: Constantina Engels
    occupation: werkster
    residence: Graauw
    relation: moeder bruidegom
  - name: Jan Makkinje
    occupation: werkman
    residence: Muiden
    relation: vader bruid
  - name: Anna Maria Gruijters
    occupation: zonder beroep
    residence: Muiden
    relation: moeder 
                """
        note: Note = Note()
        note.value = note_value
        self.event_detail.notes = [note]
        self.event_detail.parse_witnesses()

        self.assertEqual(len(self.event_detail.witnesses), 3)
        self.assertEqual(self.event_detail.witnesses[0].name, "Constantina Engels")

if __name__ == '__main__':
    unittest.main()