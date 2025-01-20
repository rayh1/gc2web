import unittest
from datetime import datetime
from Date import Date

class TestDateParseMethods(unittest.TestCase):

    def test_parse_simple_date(self):
        self.assertEqual(Date.parse_simple_date("30 JUN 1965"), "30 JUN 1965")
        self.assertEqual(Date.parse_simple_date("JUN 1965"), "JUN 1965")
        self.assertEqual(Date.parse_simple_date("1965"), "1965")
        self.assertIsNone(Date.parse_simple_date("INVALID DATE"))

    def test_parse_period_date(self):
        self.assertEqual(Date.parse_period_date("FROM 30 JUN 1965"), ("30 JUN 1965", None))
        self.assertEqual(Date.parse_period_date("TO 30 JUN 1965"), (None, "30 JUN 1965"))
        self.assertEqual(Date.parse_period_date("FROM 30 JUN 1965 TO 1 JUL 1965"), ("30 JUN 1965", "1 JUL 1965"))
        self.assertEqual(Date.parse_period_date("FROM JUN 1965"), ("JUN 1965", None))
        self.assertEqual(Date.parse_period_date("TO JUN 1965"), (None, "JUN 1965"))
        self.assertEqual(Date.parse_period_date("FROM JUN 1965 TO JUL 1965"), ("JUN 1965", "JUL 1965"))
        self.assertEqual(Date.parse_period_date("FROM 1965"), ("1965", None))
        self.assertEqual(Date.parse_period_date("TO 1965"), (None, "1965"))
        self.assertEqual(Date.parse_period_date("FROM 1965 TO 1966"), ("1965", "1966"))
        self.assertIsNone(Date.parse_period_date("INVALID DATE"))

    def test_parse_range_date(self):
        self.assertEqual(Date.parse_range_date("BET 30 JUN 1965"), "30 JUN 1965")
        self.assertEqual(Date.parse_range_date("BET JUN 1965"), "JUN 1965")
        self.assertEqual(Date.parse_range_date("BET 1965"), "1965")
        self.assertIsNone(Date.parse_range_date("INVALID DATE"))

    def test_parse_approximated_date(self):
        self.assertEqual(Date.parse_approximated_date("ABT 30 JUN 1965"), "30 JUN 1965")
        self.assertEqual(Date.parse_approximated_date("CAL JUN 1965"), "JUN 1965")
        self.assertEqual(Date.parse_approximated_date("EST 1965"), "1965")
        self.assertIsNone(Date.parse_approximated_date("INVALID DATE"))

    def test_parse_int_date(self):
        self.assertEqual(Date.parse_int_date("INT 30 JUN 1965"), "30 JUN 1965")
        self.assertEqual(Date.parse_int_date("INT JUN 1965"), "JUN 1965")
        self.assertEqual(Date.parse_int_date("INT 1965"), "1965")
        self.assertIsNone(Date.parse_int_date("INVALID DATE"))

    def test_date_simple(self):
        date = Date("30 JUN 1965")
        self.assertEqual(date.date(), datetime(1965, 6, 30))
        date = Date("JUN 1965")
        self.assertEqual(date.date(), datetime(1965, 6, 1))
        date = Date("1965")
        self.assertEqual(date.date(), datetime(1965, 1, 1))

    def test_date_period(self):
        date = Date("FROM 30 JUN 1965")
        self.assertEqual(date.date(), datetime(1965, 6, 30))
        date = Date("TO 30 JUN 1965")
        self.assertEqual(date.date(), None)
        date = Date("FROM 30 JUN 1965 TO 1 JUL 1965")
        self.assertEqual(date.date(), datetime(1965, 6, 30))
        date = Date("FROM JUN 1965")
        self.assertEqual(date.date(), datetime(1965, 6, 1))
        date = Date("TO JUN 1965")
        self.assertEqual(date.date(), None)
        date = Date("FROM JUN 1965 TO JUL 1965")
        self.assertEqual(date.date(), datetime(1965, 6, 1))
        date = Date("FROM 1965")
        self.assertEqual(date.date(), datetime(1965, 1, 1))
        date = Date("TO 1965")
        self.assertEqual(date.date(), None)
        date = Date("FROM 1965 TO 1966")
        self.assertEqual(date.date(), datetime(1965, 1, 1))

    def test_date_range(self):
        date = Date("BET 30 JUN 1965")
        self.assertEqual(date.date(), datetime(1965, 6, 30))
        date = Date("BET JUN 1965")
        self.assertEqual(date.date(), datetime(1965, 6, 1))
        date = Date("BET 1965")
        self.assertEqual(date.date(), datetime(1965, 1, 1))

    def test_date_approximated(self):
        date = Date("ABT 30 JUN 1965")
        self.assertEqual(date.date(), datetime(1965, 6, 30))
        date = Date("CAL JUN 1965")
        self.assertEqual(date.date(), datetime(1965, 6, 1))
        date = Date("EST 1965")
        self.assertEqual(date.date(), datetime(1965, 1, 1))

    def test_date_int(self):
        date = Date("INT 30 JUN 1965")
        self.assertEqual(date.date(), datetime(1965, 6, 30))
        date = Date("INT JUN 1965")
        self.assertEqual(date.date(), datetime(1965, 6, 1))
        date = Date("INT 1965")
        self.assertEqual(date.date(), datetime(1965, 1, 1))

if __name__ == '__main__':
    unittest.main()
