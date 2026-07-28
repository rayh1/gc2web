"""The site's canonical lifespan string.

Extracted from `gen_site.py` so the birthday index and the entity pages render the
same characters. [R-2] of `specs/birthday-today/birthday-today.cr.md` requires the
block to reuse the site's existing `lifespan` format verbatim — a second
implementation would let the two drift apart silently.
"""

from model.Individual import Individual


def lifespan_str(individual: Individual) -> str:
    """`(1890-1972)`, or `(1890-?)` when no death year is recorded."""
    start_date = individual.start_life.date.date()
    start_year = start_date.year if start_date and start_date.year else "?"
    end_date = individual.end_life.date.date()
    end_year = end_date.year if end_date and end_date.year else "?"

    return f"({start_year}-{end_year})"
