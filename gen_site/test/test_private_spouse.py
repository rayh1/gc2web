"""Guards gen-site PRD [R-15]: a `private: true` individual appears in no site output.

The fixture `fixtures/private_spouse.ged` holds a public man (I1) married to a private
woman (I2), with a public third person (I3) as witness at the marriage. Edge case
[E-2] of the PRD: the family still references the excluded spouse, which reaches the
husband's chronology and the witness's page.
"""

from pathlib import Path

import pytest
from birthday_index import generate_birthday_index
from model.GedcomModel import GedcomModel

from gen_site import generate_individual_pages, generate_source_pages

FIXTURE = Path(__file__).parent / "fixtures" / "private_spouse.ged"


@pytest.fixture
def fixture_model():
    model = GedcomModel()
    model.parse_file(str(FIXTURE))
    yield model
    model.clear()


@pytest.mark.xfail(
    strict=True,
    raises=AttributeError,
    reason="[R-15] open: Family.spouse() returns None for the excluded spouse and "
    "individual_link crashes on it (husband's chronology, witness's page). "
    "Remove this marker with the fix.",
)
def test_private_spouse_appears_in_no_output(fixture_model, tmp_path):
    generate_individual_pages(tmp_path)
    generate_source_pages(tmp_path)
    generate_birthday_index(
        str(FIXTURE), fixture_model, tmp_path / "birthday-index.json"
    )

    assert not (tmp_path / "I2.md").exists()
    for output in tmp_path.iterdir():
        text = output.read_text(encoding="utf-8")
        for leak in ("I2", "i2/", "Geheimina", "Verborgen"):
            assert leak not in text, f"{output.name} mentions {leak!r}"
