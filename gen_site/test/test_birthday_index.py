"""Guards the generated birthday index against `specs/birthday-today/birthday-today.cr.md`.

Everything here reads the generated index file plus the model and the raw GEDCOM
directly — no browser, no Astro build — so it runs in the same suite as
`test_liveness.py` ([R-6]).

Two kinds of assertion live here, and the difference matters:

* The **both-direction test** ([R-6]) re-derives what the index should hold from gedq
  plus `may_appear_in_aggregate`. It checks the written artifact end to end: day keys,
  ordering, serialization, staleness.
* The **property tests** ([R-7], [R-10]) never consult gedq. They read the raw GEDCOM
  and assert that whole classes of record are absent whatever gedq decides. That is
  deliberate: [R-7] adopts gedq's current exclusion of interpreted (`INT`) dates, which
  gedq's own CR-059 AC6 arguably contradicts and which is untested upstream. If a later
  gedq release starts returning those two back-computed dates, the both-direction test
  would happily follow it — these properties are what fail instead.
"""

import json
import re
import subprocess
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

from birthday_index import (
    DAYS_IN_MONTH,
    MONTH_TAGS,
    day_key,
    is_placeholder_name,
)
from model.GedcomModel import GedcomModel
from model.Liveness import may_appear_in_aggregate
from util.Lifespan import lifespan_str

GEN_SITE_DIR = Path(__file__).resolve().parent.parent
GEDCOM_FILE = GEN_SITE_DIR / "Hoofman.ged"
INDEX_FILE = GEN_SITE_DIR.parent / "src/data/birthday-index.json"

REFERENCE_YEAR = date.today().year
LIFESPAN_PATTERN = re.compile(r"^\((\d{4})-(\d{4}|\?)\)$")
# A GEDCOM date carrying an actual calendar day, e.g. `7 JUL 1881`.
DAY_AND_MONTH_PATTERN = re.compile(r"\b\d{1,2}\s+[A-Z]{3}\s+\d{4}\b")

# Every calendar day, as gedq spells them.
ALL_DAYS: list[tuple[int, int]] = [
    (month_index + 1, day)
    for month_index, month_length in enumerate(DAYS_IN_MONTH)
    for day in range(1, month_length + 1)
]


def _gedq_births(month: int, day: int) -> list[str]:
    """The xref ids gedq reports as deterministic births on one calendar day."""
    result = subprocess.run(
        [
            "gedq",
            "anniversary",
            str(GEDCOM_FILE),
            "--date",
            f"{day} {MONTH_TAGS[month - 1]}",
            "--json",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    return [
        event["entity_id"]
        for event in payload.get("events", [])
        if event.get("event") == "BIRT" and event.get("entity_id")
    ]


def _gedq_verdicts() -> dict[tuple[int, int], list[str]]:
    """gedq's birth verdict for every calendar day, computed once per test session.

    366 independent read-only subprocesses; run concurrently they take seconds rather
    than minutes, and every test class shares the one result.
    """
    global _GEDQ_BY_DAY
    if _GEDQ_BY_DAY is None:
        with ThreadPoolExecutor(max_workers=8) as pool:
            verdicts = pool.map(lambda month_day: _gedq_births(*month_day), ALL_DAYS)
        _GEDQ_BY_DAY = dict(zip(ALL_DAYS, verdicts))
    return _GEDQ_BY_DAY


_GEDQ_BY_DAY: dict[tuple[int, int], list[str]] | None = None


def _raw_birth_dates() -> dict[str, str]:
    """Every individual's raw `BIRT`/`DATE` line, straight out of the GEDCOM.

    Read from the file rather than through the model or gedq, so the [R-7] properties
    stay independent of both.
    """
    birth_dates: dict[str, str] = {}
    current_id: str | None = None
    in_birth = False

    for line in GEDCOM_FILE.read_text(encoding="utf-8-sig").splitlines():
        record = re.match(r"^0 @(\w+)@ INDI", line)
        if record:
            current_id, in_birth = record.group(1), False
            continue
        if line.startswith("0 "):
            current_id, in_birth = None, False
            continue
        if line.startswith("1 "):
            in_birth = line.startswith("1 BIRT")
        if current_id and in_birth and line.startswith("2 DATE "):
            birth_dates[current_id] = line[len("2 DATE "):].strip()

    return birth_dates


class BirthdayIndexTestCase(unittest.TestCase):
    """Shared fixtures: the generated index, the model, and gedq's per-day verdicts."""

    index: dict[str, list[dict[str, str]]]
    index_text: str
    model: GedcomModel
    by_xref_id: dict[str, object]
    gedq_by_day: dict[tuple[int, int], list[str]]

    @classmethod
    def setUpClass(cls):
        if not INDEX_FILE.exists():
            raise unittest.SkipTest(
                f"{INDEX_FILE} has not been generated; run birthday_index.py first"
            )

        cls.index_text = INDEX_FILE.read_text(encoding="utf-8")
        cls.index = json.loads(cls.index_text)

        cls.model = GedcomModel()
        cls.model.parse_file(str(GEDCOM_FILE))
        cls.by_xref_id = {
            individual.xref_id: individual for individual in cls.model.individuals
        }

        cls.gedq_by_day = _gedq_verdicts()

    # Helpers

    def entries(self) -> list[tuple[str, dict[str, str]]]:
        return [
            (key, entry) for key, entries in self.index.items() for entry in entries
        ]

    def indexed_ids(self) -> list[str]:
        return [entry["id"] for _, entry in self.entries()]

    def expected_placement(self) -> dict[str, str]:
        """Who the index should hold, and under which day key.

        gedq decides which dates are deterministic; `may_appear_in_aggregate` decides
        who may be published; [R-10] drops placeholder and stillbirth records.
        """
        placement: dict[str, str] = {}
        for (month, day), xref_ids in self.gedq_by_day.items():
            for xref_id in xref_ids:
                individual = self.by_xref_id.get(xref_id)
                if individual is None:
                    continue  # manually flagged private; removed at parse time
                if not may_appear_in_aggregate(individual, REFERENCE_YEAR):
                    continue
                if is_placeholder_name(str(individual.name)):
                    continue
                placement[xref_id] = day_key(month, day)
        return placement


class TestBothDirections(BirthdayIndexTestCase):
    """[R-6] — the index holds everyone eligible, and nobody withheld."""

    def test_no_withheld_individual_appears_anywhere(self):
        """(a) Nobody `may_appear_in_aggregate` rejects is anywhere in the file."""
        withheld = [
            individual.xref_id
            for individual in self.model.individuals
            if not may_appear_in_aggregate(individual, REFERENCE_YEAR)
        ]
        self.assertGreater(len(withheld), 0, "no withheld individuals — check the model")

        for xref_id in withheld:
            self.assertNotIn(
                xref_id,
                self.index_text,
                f"withheld individual {xref_id} appears in the shipped index",
            )

    def test_no_manually_private_individual_appears_anywhere(self):
        """(a, continued) The manual `private: true` flag is upheld too.

        These never reach `may_appear_in_aggregate` — the model drops them at parse
        time — so they need their own assertion. gedq still sees them, which is what
        makes this a real check rather than a tautology.
        """
        seen_by_gedq = {
            xref_id for xref_ids in self.gedq_by_day.values() for xref_id in xref_ids
        }
        manually_private = sorted(seen_by_gedq - set(self.by_xref_id))
        self.assertGreater(
            len(manually_private), 0, "expected gedq to see the manually private records"
        )

        for xref_id in manually_private:
            self.assertNotIn(
                xref_id,
                self.index_text,
                f"manually private individual {xref_id} appears in the shipped index",
            )

    def test_every_eligible_individual_appears_exactly_once_on_their_own_day(self):
        """(b) Everyone eligible, deterministic-dated and named is there, once."""
        expected = self.expected_placement()
        self.assertGreater(len(expected), 0, "expected a non-empty index")

        actual: dict[str, list[str]] = {}
        for key, entry in self.entries():
            actual.setdefault(entry["id"], []).append(key)

        self.assertEqual(
            sorted(actual),
            sorted(expected),
            "the index and gedq+liveness disagree about who belongs in it",
        )
        for xref_id, keys in actual.items():
            self.assertEqual(
                keys,
                [expected[xref_id]],
                f"{xref_id} should appear exactly once, under {expected[xref_id]}",
            )


class TestDateDeterminism(BirthdayIndexTestCase):
    """[R-7] — only dates gedq treats as deterministic appear."""

    def test_no_interpreted_birth_date_appears(self):
        """No `INT` birth date reaches the index, on any day.

        The two that carry a day and month — and so are the only ones a named day could
        expose — are quoted in [R-7] verbatim.
        """
        interpreted = {
            xref_id
            for xref_id, raw_date in _raw_birth_dates().items()
            if "INT" in raw_date
        }
        self.assertEqual(
            len(interpreted), 52, "the corpus's INT birth-date count has moved"
        )

        day_precise_interpreted = sorted(
            xref_id
            for xref_id, raw_date in _raw_birth_dates().items()
            if re.search(r"INT\s+\d{1,2}\s+[A-Z]{3}\s+\d{4}", raw_date)
        )
        self.assertEqual(day_precise_interpreted, ["I00129", "I00173"])

        for xref_id in sorted(interpreted):
            self.assertNotIn(
                xref_id,
                self.index_text,
                f"{xref_id} has an interpreted (INT) birth date and must not appear",
            )

    def test_no_birth_date_without_a_day_and_month_appears(self):
        """Year-only and month-only births never land on a calendar day.

        This is what keeps 1 January carrying only literal `1 JAN` births rather than
        the year-only dates the old Python parser defaulted onto that day.
        """
        without_day_and_month = sorted(
            xref_id
            for xref_id, raw_date in _raw_birth_dates().items()
            if not DAY_AND_MONTH_PATTERN.search(raw_date)
        )
        self.assertEqual(
            len(without_day_and_month),
            50,
            "the corpus's count of births with no day+month has moved",
        )

        for xref_id in without_day_and_month:
            self.assertNotIn(
                xref_id,
                self.index_text,
                f"{xref_id} has no day-and-month birth date and must not appear",
            )

    def test_a_day_precise_individual_does_appear(self):
        """Positive witness — without it the properties above pass on an empty index."""
        self.assertIn(
            "I00254",
            [entry["id"] for entry in self.index.get("07-07", [])],
            "I00254 (7 JUL 1881) should appear under 7 July",
        )


class TestPlaceholderNames(BirthdayIndexTestCase):
    """[R-10] — placeholder-named and stillbirth records never appear."""

    def test_no_entry_carries_a_placeholder_name(self):
        for key, entry in self.entries():
            self.assertFalse(
                is_placeholder_name(entry["name"]),
                f"{entry['id']} ({entry['name']}) on {key} is a placeholder record",
            )

    def test_the_six_days_emptied_by_the_rule_are_absent(self):
        """1 Jan, 7 Feb, 18 Mar, 6 Jun, 20 Jun and 29 Jul lose their only entry."""
        for key in ("01-01", "02-07", "03-18", "06-06", "06-20", "07-29"):
            self.assertNotIn(
                key,
                self.index,
                f"{key} should have been emptied by the placeholder rule",
            )


class TestIndexShape(BirthdayIndexTestCase):
    """[R-8], [R-2] and the locked ordering."""

    def test_only_days_with_content_are_present(self):
        for key, entries in self.index.items():
            self.assertGreater(len(entries), 0, f"{key} is present but empty")

    def test_keys_are_zero_padded_month_day(self):
        for key in self.index:
            self.assertRegex(key, r"^\d{2}-\d{2}$")

    def test_29_february_is_absent(self):
        """No eligible individual has a 29 February birthday, so the day has no key."""
        self.assertNotIn("02-29", self.index)

    def test_lifespan_reuses_the_sites_own_format(self):
        """[R-2] — verbatim the string the entity pages carry."""
        for key, entry in self.entries():
            self.assertRegex(
                entry["lifespan"],
                LIFESPAN_PATTERN,
                f"{entry['id']} on {key} has a malformed lifespan",
            )
            individual = self.by_xref_id[entry["id"]]
            self.assertEqual(entry["lifespan"], lifespan_str(individual))

    def test_names_carry_no_gedcom_slashes(self):
        for _, entry in self.entries():
            self.assertNotIn("/", entry["name"])

    def test_entries_on_a_day_are_ordered_oldest_first(self):
        """Locked: ascending birth year, which [R-2]'s worked example fixed."""
        for key, entries in self.index.items():
            years = [
                int(LIFESPAN_PATTERN.match(entry["lifespan"]).group(1))
                for entry in entries
            ]
            self.assertEqual(years, sorted(years), f"{key} is not oldest-first")

    def test_the_worked_example_renders_as_confirmed(self):
        """[R-2]'s worked example, verbatim: 9 March, three entries, in order."""
        self.assertEqual(
            [
                (entry["name"], entry["lifespan"], f"/entity/{entry['id'].lower()}/")
                for entry in self.index["03-09"]
            ],
            [
                ("Pieter Hoofman", "(1833-1874)", "/entity/i00013/"),
                ("Helena Louisa Walters", "(1873-1922)", "/entity/i00096/"),
                ("Anna Maria Christina Hoofman", "(1893-?)", "/entity/i00012/"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
