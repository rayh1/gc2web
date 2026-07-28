"""Mechanical gate for constitution rule [C-1].

[C-1]: "Any newly added aggregate output — a page, list, or feed that selects a set of
individuals — excludes individuals classified LIVING/PRIVATE by [C-2]."

The rule was filed reviewer-assisted because "which generated pages count as aggregate
output" had no mechanical handle. This test supplies one, in the general form the
constitution's own promotion note proposed: assert over the **built site** that no
non-entity route in `dist/` references an entity id from the ineligible set.

Why that form and not a test over one feature's artifact: a per-feature assertion only
guards the surface it was written for, so the next aggregate page escapes it silently —
the no-narrowing objection that kept [C-1] reviewer-assisted. Scanning everything except
an explicit exemption list inverts the default: a new route is covered the day it is
built, and adding an exemption is a visible edit to this file.

The exemptions are exactly the four surfaces [C-1] names as predating the rule, plus the
sitemaps, which mechanically mirror those routes rather than selecting individuals of
their own. Everything else is scanned — including `index.html`, where the birthday block
lives, and the 511 generated source pages.

Requires a built site. Run `npm run build` first; the [C-1] Check clause does.
"""

import re
import unittest
from datetime import date
from pathlib import Path

from model.GedcomModel import GedcomModel
from model.Liveness import LivenessStatus, classify

GEN_SITE_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = GEN_SITE_DIR.parent
GEDCOM_FILE = GEN_SITE_DIR / "Hoofman.ged"
DIST_DIR = REPO_ROOT / "dist"

REFERENCE_YEAR = date.today().year

# Text formats a generated id could actually surface in. Binary assets (images, fonts)
# are skipped — an xref id cannot be "referenced" from one in any way a reader could use.
SCANNED_SUFFIXES = frozenset({".html", ".xml", ".js", ".json", ".css", ".txt", ".svg"})

# The four surfaces [C-1] names verbatim as predating the rule and deliberately in scope
# for publication, plus the sitemaps. Adding to this list is a deliberate, reviewable act.
EXEMPT_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"^entity/i\d+/index\.html$", "per-person entity page"),
    (r"^entity/\d+/index\.html$", "paginated entity index (entity/[...page].astro)"),
    (r"^entity/index\.html$", "paginated entity index, first page"),
    (r"^search/index\.html$", "search index (Searchbar.astro)"),
    (r"^rss\.xml$", "RSS feed (rss.xml.js)"),
    (r"^sitemap[-\w]*\.xml$", "sitemap — mirrors the routes above, selects nobody itself"),
)


def is_exempt(relative_path: str) -> str | None:
    """The reason this route is exempt, or None when it must be scanned."""
    for pattern, reason in EXEMPT_PATTERNS:
        if re.match(pattern, relative_path):
            return reason
    return None


def ineligible_xref_ids() -> list[str]:
    """The individuals [C-2] classifies LIVING/PRIVATE — the set [C-1] withholds."""
    model = GedcomModel()
    model.parse_file(str(GEDCOM_FILE))
    return sorted(
        individual.xref_id
        for individual in model.individuals
        if classify(individual, REFERENCE_YEAR) is LivenessStatus.LIVING_PRIVATE
    )


class TestAggregateOutputPrivacy(unittest.TestCase):
    """[C-1] over the built site."""

    @classmethod
    def setUpClass(cls):
        if not DIST_DIR.is_dir():
            raise AssertionError(
                f"{DIST_DIR} does not exist — [C-1] is a claim about the BUILT site and "
                "cannot be checked without one. Run `npm run build` first."
            )
        cls.ineligible = ineligible_xref_ids()
        cls.scanned: list[Path] = []
        cls.exempt: list[tuple[str, str]] = []
        for path in sorted(DIST_DIR.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in SCANNED_SUFFIXES:
                continue
            relative = path.relative_to(DIST_DIR).as_posix()
            reason = is_exempt(relative)
            if reason:
                cls.exempt.append((relative, reason))
            else:
                cls.scanned.append(path)

    def test_the_ineligible_set_is_not_empty(self):
        """Guards against a vacuous pass: no withheld people, nothing to catch."""
        self.assertGreater(
            len(self.ineligible), 0, "no LIVING/PRIVATE individuals — check the model"
        )

    def test_something_is_actually_scanned(self):
        """Guards against the exemption list swallowing the whole site."""
        self.assertGreater(len(self.scanned), 0, "every route was exempted")
        scanned_names = {path.relative_to(DIST_DIR).as_posix() for path in self.scanned}
        self.assertIn(
            "index.html",
            scanned_names,
            "the homepage carries the birthday block and must never be exempt",
        )

    def test_no_non_entity_route_names_a_withheld_individual(self):
        """The rule itself."""
        pattern = re.compile(
            "|".join(re.escape(xref_id) for xref_id in self.ineligible), re.IGNORECASE
        )
        violations: list[str] = []
        for path in self.scanned:
            for match in set(pattern.findall(path.read_text(encoding="utf-8", errors="ignore"))):
                violations.append(f"{path.relative_to(DIST_DIR).as_posix()} references {match}")

        self.assertEqual(
            violations,
            [],
            "aggregate output names individuals [C-2] classifies LIVING/PRIVATE:\n  "
            + "\n  ".join(sorted(violations)),
        )


if __name__ == "__main__":
    unittest.main()
