"""Guards gen-site PRD [R-15]: a `private: true` individual appears in no site output.

The fixture `fixtures/private_spouse.ged` holds a public man (I1) married to a private
woman (I2, with a recorded death date), with a public third person (I3) as witness at
the marriage. Edge case [E-2] of the PRD: the family still references the excluded
spouse, which reaches the husband's chronology and the witness's page.

The fixture `fixtures/single_partner.ged` holds the same situation without a private
person: a family with one partner (I1) and no one on the other side, with a dated
marriage witnessed by a public I3. `Family.spouse()` returns None there as well.
"""

import re
from pathlib import Path

import pytest
from birthday_index import generate_birthday_index
from model.GedcomModel import GedcomModel

from gen_site import generate_individual_pages, generate_source_pages

FIXTURES = Path(__file__).parent / "fixtures"
FIXTURE = FIXTURES / "private_spouse.ged"
SINGLE_PARTNER_FIXTURE = FIXTURES / "single_partner.ged"

# A chronology line: `- 12-05-1875 (<i>25</i>): Huwelijk`, the age being optional.
CHRONOLOGY_LINE = re.compile(r"^- (\d{2}-\d{2}-\d{4})(?: \(<i>[^<]*</i>\))?: (.*)$")
# A Markdown link, `[text](target)`; person pages link people this way.
MARKDOWN_LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")
# An HTML link; source references are rendered this way.
HTML_HREF = re.compile(r'href="([^"]*)"')


@pytest.fixture
def fixture_model():
    model = GedcomModel()
    model.parse_file(str(FIXTURE))
    yield model
    model.clear()


@pytest.fixture
def single_partner_model():
    model = GedcomModel()
    model.parse_file(str(SINGLE_PARTNER_FIXTURE))
    yield model
    model.clear()


def section_lines(page: str, heading: str) -> list[str]:
    """The lines under `### <heading>`, up to the next `### ` heading."""
    lines = page.splitlines()
    start = lines.index(f"### {heading}") + 1
    end = next(
        (i for i in range(start, len(lines)) if lines[i].startswith("### ")),
        len(lines),
    )
    return lines[start:end]


def chronology(page: str) -> list[tuple[str, str]]:
    """Each chronology line as (date, description)."""
    entries = []
    for line in section_lines(page, "Chronologie"):
        if not line.strip():
            continue
        match = CHRONOLOGY_LINE.match(line)
        assert match, f"unexpected chronology line {line!r}"
        entries.append((match.group(1), match.group(2)))
    return entries


def marriage_witness_entries(page: str) -> list[str]:
    return [
        line
        for line in section_lines(page, "Getuige bij")
        if line.startswith("- Huwelijk ")
    ]


def assert_links_only(entry: str, name: str, target: str) -> None:
    """The entry links exactly one person, `name` at `target`; other links are sources."""
    assert MARKDOWN_LINK.findall(entry) == [(name, target)], entry
    for href in HTML_HREF.findall(entry):
        assert re.fullmatch(r"\.\./s\d+/", href), f"{entry!r} links {href!r}"


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


def test_public_spouse_keeps_marriage_without_private_partner(fixture_model, tmp_path):
    generate_individual_pages(tmp_path)

    entries = chronology((tmp_path / "I1.md").read_text(encoding="utf-8"))

    assert [e for e in entries if e[0] == "12-05-1875"] == [("12-05-1875", "Huwelijk")]
    # I2 has a recorded death date (4 FEB 1890), so this line would be produced
    # if the private partner's death were not withheld.
    assert not any(
        description.startswith("Overlijden partner") for _, description in entries
    ), entries
    assert not any(d == "04-02-1890" for d, _ in entries), entries


def test_witness_entry_names_only_public_partner(fixture_model, tmp_path):
    generate_individual_pages(tmp_path)

    page = (tmp_path / "I3.md").read_text(encoding="utf-8")
    entries = marriage_witness_entries(page)

    assert len(entries) == 1, entries
    assert " op 12 MAY 1875 " in entries[0], entries[0]
    assert_links_only(entries[0], "Johannes Publiek", "../i1/")


def test_family_without_other_partner(single_partner_model, tmp_path):
    generate_individual_pages(tmp_path)
    generate_source_pages(tmp_path)

    partner_entries = chronology((tmp_path / "I1.md").read_text(encoding="utf-8"))
    assert [e for e in partner_entries if e[0] == "20-06-1876"] == [
        ("20-06-1876", "Huwelijk")
    ]
    assert not any(
        description.startswith("Overlijden partner")
        for _, description in partner_entries
    ), partner_entries

    witness_entries = marriage_witness_entries(
        (tmp_path / "I3.md").read_text(encoding="utf-8")
    )
    assert len(witness_entries) == 1, witness_entries
    assert " op 20 JUN 1876 " in witness_entries[0], witness_entries[0]
    assert_links_only(witness_entries[0], "Cornelis Alleen", "../i1/")
