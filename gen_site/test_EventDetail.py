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
    
    def test_parse_timestamp_with_valid_data(self):
        note_value = """
---
timestamp: "2023-01-01 12:00:00"
            """
        note = Note()
        note.value = note_value
        self.event_detail.notes = [note]
        self.event_detail.parse_timestamp()
        
        self.assertEqual(self.event_detail.timestamp, "2023-01-01 12:00:00")

    def test_parse_timestamp_with_invalid_yaml(self):
        note_value = "invalid: yaml: content:"
        note = Note()
        note.value = note_value
        self.event_detail.notes = [note]
        self.event_detail.parse_timestamp()
        
        self.assertIsNone(self.event_detail.timestamp)

    def test_parse_timestamp_with_missing_timestamp(self):
        note_value = """
---
other_field: "some value"
            """
        note = Note()
        note.value = note_value
        self.event_detail.notes = [note]
        self.event_detail.parse_timestamp()
        
        self.assertIsNone(self.event_detail.timestamp)

    def test_parse_timestamp_with_empty_note(self):
        note = Note()
        note.value = None
        self.event_detail.notes = [note]
        self.event_detail.parse_timestamp()
        
        self.assertIsNone(self.event_detail.timestamp)

    def test_parse_timestamp_without_notes(self):
        self.event_detail.notes = []
        self.event_detail.parse_timestamp()
        
        self.assertIsNone(self.event_detail.timestamp)

    def test_parse_timestamp_problem(self):
        note_value = """
---
timestamp: "4:00"
            """
        note = Note()
        note.value = note_value
        self.event_detail.notes = [note]
        self.event_detail.parse_timestamp()
        
        print(self.event_detail.timestamp)
        self.assertEqual(self.event_detail.timestamp, "4:00")


if __name__ == '__main__':
    unittest.main()