import unittest
from datetime import datetime
from Date import Date

class TestDate(unittest.TestCase):
    def test_simple_date(self):
        date = Date("01 JAN 2000")
        self.assertEqual(date.date(), datetime(2000, 1, 1))

    def test_date_period(self):
        date = Date("FROM 01 JAN 2000 TO 31 DEC 2000")
        self.assertEqual(date.date(), datetime(2000, 1, 1))

    def test_date_range(self):
        date = Date("BET 01 JAN 2000 AND 31 DEC 2000")
        self.assertEqual(date.date(), datetime(2000, 1, 1))

    def test_date_approximated(self):
        date = Date("ABT 01 JAN 2000")
        self.assertEqual(date.date(), datetime(2000, 1, 1))

    def test_date_int(self):
        date = Date("INT 2000 (2088 - 88)")
        self.assertEqual(date.date(), datetime(2000, 1, 1))

    def test_invalid_date(self):
        date = Date("invalid date")
        self.assertIsNone(date.date())

    def test_empty_date(self):
        date = Date(None)
        self.assertIsNone(date.date())

if __name__ == "__main__":
    unittest.main()
