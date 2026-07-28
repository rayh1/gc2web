"""Pins the liveness thresholds normatively stated in specs/constitution.md [C-2].

Every threshold is checked on BOTH sides of its boundary, so changing a value in
model/Liveness.py without changing the rule makes this test fail.
"""

import unittest

from model.Date import Date
from model.EventDetail import EventDetail
from model.Liveness import (
    EVENT_RECENCY_YEARS,
    LIVING_MAX_AGE_YEARS,
    LivenessStatus,
    classify,
    may_appear_in_aggregate,
)
from model.Place import Place

REFERENCE_YEAR = 2026


def event(date_value: str | None = None, place_value: str | None = None) -> EventDetail:
    detail = EventDetail()
    if date_value is not None:
        detail.date = Date(date_value)
    if place_value is not None:
        detail.place = Place(place_value)
    return detail


class FakeFamily:
    def __init__(self, marriage=None, children=None):
        self.marriage = marriage if marriage is not None else EventDetail()
        self.children = children if children is not None else []


class FakeIndividual:
    def __init__(self, birth=None, death=None, burial=None, fams=None, private=False):
        self.birth = birth if birth is not None else EventDetail()
        self.death = death if death is not None else EventDetail()
        self.burial = burial if burial is not None else EventDetail()
        self.fams = fams if fams is not None else []
        self.__private = private

    def is_private(self) -> bool:
        return self.__private


def child_born(year: int) -> FakeIndividual:
    return FakeIndividual(birth=event(str(year)))


class TestLivenessThresholds(unittest.TestCase):
    """The three branches and their exact boundaries.

    Boundary years below are LITERAL on purpose. Deriving them from the constants
    (`REFERENCE_YEAR - LIVING_MAX_AGE_YEARS`) makes the test move with the code, so a
    changed threshold stays green — verified: 110 -> 100 passed 18/18 before this was
    pinned. Literal years plus the explicit constant assertions are what make a
    threshold change detectable.
    """

    def classify(self, individual) -> LivenessStatus:
        return classify(individual, REFERENCE_YEAR)

    def test_thresholds_match_the_constitution(self):
        """[C-2] states 110 and 95; the code must not drift from the rule."""
        self.assertEqual(LIVING_MAX_AGE_YEARS, 110)
        self.assertEqual(EVENT_RECENCY_YEARS, 95)

    # Branch 1 — death or burial evidence wins outright.

    def test_death_date_is_deceased(self):
        self.assertEqual(
            self.classify(FakeIndividual(death=event("12 MAR 1901"))),
            LivenessStatus.DECEASED,
        )

    def test_burial_place_without_a_date_is_still_evidence(self):
        self.assertEqual(
            self.classify(FakeIndividual(burial=event(place_value="Amsterdam"))),
            LivenessStatus.DECEASED,
        )

    def test_source_citation_alone_is_death_evidence(self):
        """A `1 DEAT` whose only sub-line is `2 SOUR @S…@` — undated but attested."""
        death = EventDetail()
        death.add_source_id("@S00492@")
        self.assertEqual(self.classify(FakeIndividual(death=death)), LivenessStatus.DECEASED)

    def test_death_evidence_outranks_a_recent_birth(self):
        recent = FakeIndividual(birth=event("1990"), death=event("2020"))
        self.assertEqual(self.classify(recent), LivenessStatus.DECEASED)

    # Branch 2 — birth threshold, checked on both sides.

    def test_born_exactly_at_the_age_threshold_is_living(self):
        born = 1916  # REFERENCE_YEAR - 110, pinned literally
        self.assertEqual(
            self.classify(FakeIndividual(birth=event(str(born)))),
            LivenessStatus.LIVING_PRIVATE,
        )

    def test_born_one_year_beyond_the_age_threshold_is_presumed_deceased(self):
        born = 1915  # one year past the 110 boundary, pinned literally
        self.assertEqual(
            self.classify(FakeIndividual(birth=event(str(born)))),
            LivenessStatus.PRESUMED_DECEASED,
        )

    # Branch 2 — marriage recency, both sides. These are PROXIES for an unknown birth
    # date, so every case below deliberately leaves the birth unset; with a known birth
    # year they must not fire at all (see the proxy-scoping tests further down).

    def test_married_exactly_at_the_recency_threshold_is_living(self):
        married = 1931  # REFERENCE_YEAR - 95, pinned literally
        individual = FakeIndividual(fams=[FakeFamily(marriage=event(str(married)))])
        self.assertEqual(self.classify(individual), LivenessStatus.LIVING_PRIVATE)

    def test_married_one_year_beyond_the_recency_threshold_is_presumed_deceased(self):
        married = 1930  # one year past the 95 boundary, pinned literally
        individual = FakeIndividual(fams=[FakeFamily(marriage=event(str(married)))])
        self.assertEqual(self.classify(individual), LivenessStatus.PRESUMED_DECEASED)

    # Branch 2 — child-birth recency, both sides. Same proxy scoping.

    def test_child_born_exactly_at_the_recency_threshold_is_living(self):
        born = 1931  # REFERENCE_YEAR - 95, pinned literally
        individual = FakeIndividual(fams=[FakeFamily(children=[child_born(born)])])
        self.assertEqual(self.classify(individual), LivenessStatus.LIVING_PRIVATE)

    def test_child_born_one_year_beyond_the_recency_threshold_is_presumed_deceased(self):
        born = 1930  # one year past the 95 boundary, pinned literally
        individual = FakeIndividual(fams=[FakeFamily(children=[child_born(born)])])
        self.assertEqual(self.classify(individual), LivenessStatus.PRESUMED_DECEASED)

    def test_most_recent_event_decides_when_several_exist(self):
        individual = FakeIndividual(
            fams=[
                FakeFamily(marriage=event("1880")),
                FakeFamily(marriage=event("1931")),
            ],
        )
        self.assertEqual(self.classify(individual), LivenessStatus.LIVING_PRIVATE)

    # The rule says "a child was born 95 years ago or less" — ANY child, in any family.
    # Both tests below put the OLD child first on purpose: a traversal that stops at the
    # first family or the first child reads 1890, calls the individual PRESUMED DECEASED,
    # and publishes them. Added 2026-07-28 after a calibration re-audit found that plant
    # passing 22/22 — the marriage branch was covered across families, this one was not.

    def test_the_most_recent_child_decides_across_families(self):
        individual = FakeIndividual(
            fams=[
                FakeFamily(children=[child_born(1890)]),
                FakeFamily(children=[child_born(1935)]),
            ],
        )
        self.assertEqual(self.classify(individual), LivenessStatus.LIVING_PRIVATE)

    def test_the_most_recent_child_decides_within_one_family(self):
        individual = FakeIndividual(
            fams=[FakeFamily(children=[child_born(1890), child_born(1935)])],
        )
        self.assertEqual(self.classify(individual), LivenessStatus.LIVING_PRIVATE)

    # Branch 2 — the proxy scoping itself: a KNOWN birth year settles the question and
    # a late marriage or child does not override it. This is the 19-person cohort in
    # Hoofman.ged (born 1892–1912) that the earlier reading withheld at age 114+.

    def test_known_old_birth_is_not_overridden_by_a_recent_child(self):
        individual = FakeIndividual(
            birth=event("1902"), fams=[FakeFamily(children=[child_born(1935)])]
        )
        self.assertEqual(self.classify(individual), LivenessStatus.PRESUMED_DECEASED)

    def test_known_old_birth_is_not_overridden_by_a_recent_marriage(self):
        individual = FakeIndividual(
            birth=event("1902"), fams=[FakeFamily(marriage=event("1935"))]
        )
        self.assertEqual(self.classify(individual), LivenessStatus.PRESUMED_DECEASED)

    def test_known_recent_birth_wins_regardless_of_old_events(self):
        individual = FakeIndividual(
            birth=event("1916"), fams=[FakeFamily(marriage=event("1800"))]
        )
        self.assertEqual(self.classify(individual), LivenessStatus.LIVING_PRIVATE)

    # Branch 2 — the no-dates case.

    def test_no_usable_dates_at_all_is_living(self):
        self.assertEqual(
            self.classify(FakeIndividual()), LivenessStatus.LIVING_PRIVATE
        )

    def test_an_undated_marriage_alone_is_still_no_usable_dates(self):
        individual = FakeIndividual(fams=[FakeFamily(marriage=event())])
        self.assertEqual(self.classify(individual), LivenessStatus.LIVING_PRIVATE)

    # Branch 3.

    def test_old_birth_with_no_recent_events_is_presumed_deceased(self):
        individual = FakeIndividual(
            birth=event("1820"), fams=[FakeFamily(marriage=event("1845"))]
        )
        self.assertEqual(self.classify(individual), LivenessStatus.PRESUMED_DECEASED)


class TestAggregateGate(unittest.TestCase):
    """may_appear_in_aggregate composes liveness with the manual privacy flag."""

    def test_presumed_deceased_may_appear(self):
        individual = FakeIndividual(birth=event("1820"))
        self.assertTrue(may_appear_in_aggregate(individual, REFERENCE_YEAR))

    def test_deceased_may_appear(self):
        individual = FakeIndividual(death=event("1901"))
        self.assertTrue(may_appear_in_aggregate(individual, REFERENCE_YEAR))

    def test_living_may_not_appear(self):
        individual = FakeIndividual(birth=event("1990"))
        self.assertFalse(may_appear_in_aggregate(individual, REFERENCE_YEAR))

    def test_manually_private_may_not_appear_even_when_deceased(self):
        individual = FakeIndividual(death=event("1901"), private=True)
        self.assertFalse(may_appear_in_aggregate(individual, REFERENCE_YEAR))


if __name__ == "__main__":
    unittest.main()
