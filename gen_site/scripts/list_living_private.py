"""List the individuals that aggregate output must withhold.

The mechanical assist behind constitution rule [C-1]: prints one xref id per line for
every individual `model.Liveness` classifies LIVING_PRIVATE, so a reviewer can check a
new list, feed, or roll-up page against a concrete set instead of eyeballing it.

Run from the `gen_site/` directory:

    env -u VIRTUAL_ENV uv run python scripts/list_living_private.py [gedcom_file]
"""

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from model.GedcomModel import GedcomModel  # noqa: E402
from model.Liveness import LivenessStatus, classify  # noqa: E402


def main(argv: list[str]) -> int:
    gedcom_file = argv[1] if len(argv) > 1 else "Hoofman.ged"
    reference_year = date.today().year

    model = GedcomModel()
    model.parse_file(gedcom_file)

    withheld = [
        individual
        for individual in model.individuals
        if classify(individual, reference_year) is LivenessStatus.LIVING_PRIVATE
    ]

    for individual in sorted(withheld, key=lambda i: i.xref_id):
        print(individual.xref_id)

    print(
        f"\n{len(withheld)} of {len(model.individuals)} published individuals are "
        f"LIVING/PRIVATE (reference year {reference_year})",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
