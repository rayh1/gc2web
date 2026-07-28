"""Liveness classification — who may appear in aggregate output.

Decides whether an individual is plausibly still living and must therefore be withheld
from aggregate output (lists, feeds, roll-up pages).

This COMPOSES WITH, and never replaces, the manual privacy flag: an individual carrying
`private: true` in a note is already removed from the model entirely by
`GedcomModel.__exclude_privates` (via `NotesMixin.is_private`) and never reaches any
output at all. This classifier withholds a further set from *aggregate* output only —
their own entity page is unaffected.

The thresholds below are normative and are mirrored in `specs/constitution.md` [C-2].
Changing a value here without changing the rule (or the reverse) is a constitution
violation; `tests/test_liveness.py` is what makes that detectable.
"""

from enum import Enum


# Normative thresholds — mirrored in specs/constitution.md [C-2].
LIVING_MAX_AGE_YEARS = 110
EVENT_RECENCY_YEARS = 95


class LivenessStatus(Enum):
    """Outcome of the three-branch classification."""

    DECEASED = "DECEASED"
    PRESUMED_DECEASED = "PRESUMED_DECEASED"
    LIVING_PRIVATE = "LIVING_PRIVATE"


def _has_evidence(event) -> bool:
    """True when an event carries any content at all.

    A value, a date, a place, a source citation, or a note all count: the rule is
    "any death or burial evidence, dated or not", so a `1 DEAT` whose only sub-line is
    `2 SOUR @S00492@` — a death attested by a document but never dated — is evidence.
    Hoofman.ged contains two such individuals (@I00310@, @I00312@).

    Accepted gap: a tag with NO sub-lines at all (a truly bare `1 DEAT`) is
    indistinguishable from an absent tag in this model and reads as no evidence.
    Hoofman.ged contains zero of those.
    """
    if event is None:
        return False
    if event.value:
        return True
    date = event.date
    if date is not None and date.value:
        return True
    place = event.place
    if place is not None and place.value:
        return True
    return bool(event.source_ids or event.notes)


def _year(event) -> int | None:
    """The four-digit year of an event, or None when it has no parseable date."""
    if event is None:
        return None
    date = event.date
    if date is None:
        return None
    parsed = date.date()
    return parsed.year if parsed else None


def _marriage_years(individual) -> list[int]:
    years = []
    for family in individual.fams:
        year = _year(family.marriage)
        if year is not None:
            years.append(year)
    return years


def _child_birth_years(individual) -> list[int]:
    years = []
    for family in individual.fams:
        for child in family.children:
            year = _year(child.birth)
            if year is not None:
                years.append(year)
    return years


def classify(individual, reference_year: int) -> LivenessStatus:
    """Classify an individual as DECEASED, PRESUMED_DECEASED, or LIVING_PRIVATE.

    1. Death or burial evidence             -> DECEASED
    2. Born <= LIVING_MAX_AGE_YEARS ago,
       or no date a year can be parsed from -> LIVING_PRIVATE
       or, WHEN THE BIRTH YEAR IS UNKNOWN, married or had a child
       <= EVENT_RECENCY_YEARS ago           -> LIVING_PRIVATE
    3. Otherwise                             -> PRESUMED_DECEASED

    Marriage and child recency are PROXIES for a birth date we do not have. A known
    birth year beyond LIVING_MAX_AGE_YEARS settles the question on its own, and a late
    marriage or a late child does not override it — otherwise someone born in 1902 who
    had a child in 1935 would be withheld at age 124. Nineteen individuals in
    Hoofman.ged (born 1892–1912) sat in exactly that position under the earlier reading.
    """
    if _has_evidence(individual.death) or _has_evidence(individual.burial):
        return LivenessStatus.DECEASED

    birth_year = _year(individual.birth)
    marriage_years = _marriage_years(individual)
    child_birth_years = _child_birth_years(individual)

    if birth_year is None and not marriage_years and not child_birth_years:
        return LivenessStatus.LIVING_PRIVATE

    if birth_year is not None:
        if reference_year - birth_year <= LIVING_MAX_AGE_YEARS:
            return LivenessStatus.LIVING_PRIVATE
        return LivenessStatus.PRESUMED_DECEASED

    if marriage_years and reference_year - max(marriage_years) <= EVENT_RECENCY_YEARS:
        return LivenessStatus.LIVING_PRIVATE
    if child_birth_years and reference_year - max(child_birth_years) <= EVENT_RECENCY_YEARS:
        return LivenessStatus.LIVING_PRIVATE

    return LivenessStatus.PRESUMED_DECEASED


def may_appear_in_aggregate(individual, reference_year: int) -> bool:
    """The single selection path every aggregate output must route through.

    An aggregate page, list, or feed that enumerates individuals filters them through
    this function; anything selecting individuals by any other means is a [C-1]
    violation, whatever the rendered result happens to look like.
    """
    if individual.is_private():
        return False
    return classify(individual, reference_year) is not LivenessStatus.LIVING_PRIVATE
