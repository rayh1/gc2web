"""Generate the birthday index shipped to the browser.

Implements the generation half of `specs/birthday-today/birthday-today.cr.md`.

The site is built once into static files, so "who was born today" cannot be baked in
without a daily rebuild. Instead this module emits an index of every calendar day that
has at least one eligible individual, and the homepage block picks today's key out of
it in the visitor's own browser.

Two filters decide who reaches the file, in this order:

1. **Date determinism — gedq's call, not ours.** A day's candidates are exactly the
   `BIRT` rows `gedq anniversary --date "<D> <MON>" --json` returns for it. Year-only,
   month-only and interpreted (`INT`) dates are therefore absent because gedq already
   excludes them ([R-7]). gc2web deliberately does not reimplement that judgement.
2. **Placeholder and stillbirth names — [R-10].** Records whose given name is one of
   `N.N.`, `NN`, `N` or `Levenloos` are not people the block should name.

Days that end up with nobody are left out of the file entirely ([R-8]); the client
treats a missing key as an empty day.
"""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from model.GedcomModel import GedcomModel
from model.Individual import Individual
from util.Lifespan import lifespan_str

# Every calendar day is queried, 29 February included — [R-9] requires generation to
# survive all 366 of them.
MONTH_TAGS: tuple[str, ...] = (
    "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC",
)
DAYS_IN_MONTH: tuple[int, ...] = (31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

# Verbatim from [R-10]; these are the forms present in the corpus, matched as whole
# leading tokens so that a real name like "Nico" is never caught by "N".
PLACEHOLDER_GIVEN_NAMES: frozenset[str] = frozenset({"N.N.", "NN", "N", "Levenloos"})


def is_placeholder_name(name: str) -> bool:
    """True when the given name marks a placeholder or a stillbirth ([R-10])."""
    tokens = name.split()
    return bool(tokens) and tokens[0] in PLACEHOLDER_GIVEN_NAMES


def day_key(month: int, day: int) -> str:
    """The index key for a calendar day: zero-padded `MM-DD`, year-free."""
    return f"{month:02d}-{day:02d}"


def _birth_ids_on(gedcom_file: str, month_index: int, day: int) -> list[str]:
    """The xref ids gedq reports as deterministic births on one calendar day."""
    date_argument = f"{day} {MONTH_TAGS[month_index]}"
    command = [
        "gedq",
        "anniversary",
        str(gedcom_file),
        "--date",
        date_argument,
        "--json",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise RuntimeError(f"gedq anniversary failed for {date_argument!r}: {message}")

    payload = json.loads(result.stdout)
    return [
        event["entity_id"]
        for event in payload.get("events", [])
        if event.get("event") == "BIRT" and event.get("entity_id")
    ]


def _birth_year(individual: Individual) -> int:
    """The birth year of an index candidate.

    Every candidate reaches this function through gedq's determinism filter, so a
    parseable year is guaranteed; the fallback only keeps sorting total if that ever
    stops holding.
    """
    start_date = individual.start_life.date.date()
    return start_date.year if start_date and start_date.year else 0


def build_birthday_index(
    gedcom_file: str,
    model: GedcomModel,
) -> dict[str, list[dict[str, str]]]:
    """Build the index: `MM-DD` -> entries, oldest first, content-bearing days only."""
    by_xref_id = {individual.xref_id: individual for individual in model.individuals}
    index: dict[str, list[dict[str, str]]] = {}

    for month_index, month_length in enumerate(DAYS_IN_MONTH):
        for day in range(1, month_length + 1):
            candidates: list[tuple[int, str, dict[str, str]]] = []

            for xref_id in _birth_ids_on(gedcom_file, month_index, day):
                individual = by_xref_id.get(xref_id)
                if individual is None:
                    # Manually flagged private: already removed from the model.
                    continue

                name = str(individual.name)
                if is_placeholder_name(name):
                    continue

                candidates.append((
                    _birth_year(individual),
                    xref_id,
                    {
                        "id": xref_id,
                        "name": name,
                        "lifespan": lifespan_str(individual),
                    },
                ))

            if not candidates:
                # [R-8]: a day with nothing on it gets no key at all.
                continue

            # Oldest first; the xref id breaks ties so the file is byte-stable.
            candidates.sort(key=lambda candidate: (candidate[0], candidate[1]))
            index[day_key(month_index + 1, day)] = [entry for _, _, entry in candidates]

    return index


def generate_birthday_index(
    gedcom_file: str,
    model: GedcomModel,
    output_path: Path,
) -> dict[str, list[dict[str, str]]]:
    """Build the index and write it, returning what was written."""
    index = build_birthday_index(gedcom_file, model)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return index


def main(argv: list[str]) -> int:
    """Regenerate the index on its own, without a full site generation run.

    [R-9] asks that generation complete without error on every day it queries, so the
    index is runnable — and therefore checkable — as its own command:

        env -u VIRTUAL_ENV uv run python birthday_index.py [gedcom_file]
    """
    gedcom_file = argv[1] if len(argv) > 1 else "Hoofman.ged"
    default_output = Path(__file__).resolve().parent.parent / "src/data/birthday-index.json"
    output_path = Path(argv[2]) if len(argv) > 2 else default_output

    model = GedcomModel()
    model.parse_file(gedcom_file)

    index = generate_birthday_index(gedcom_file, model, output_path)

    entries = sum(len(day) for day in index.values())
    print(
        f"{entries} entries across {len(index)} days -> {output_path}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
