import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from model.Association import Association
from model.EventDetail import EventDetail
from model.Family import Family
from model.Individual import Individual
from model.Name import Name
from model.Note import Note
from model.Repository import Repository
from model.Source import Source


REQUIRED_GEDQ_VERSION = (2, 0, 0)


@dataclass(frozen=True)
class GedqDataset:
    individuals: list[dict]
    families: list[dict]
    sources: list[dict]
    repositories: list[dict]


INDIVIDUAL_SINGLE_EVENT_TAGS = {
    "BIRT": "birth",
    "DEAT": "death",
    "CHR": "baptism",
    "BURI": "burial",
}


INDIVIDUAL_MULTI_EVENT_TAGS = {
    "OCCU": "add_occupation",
    "RESI": "add_residence",
    "FACT": "add_fact",
    "DSCR": "add_description",
}


def parse_version(raw_version: str) -> tuple[int, int, int]:
    version_text = raw_version.strip().split()[0]
    parts = version_text.split(".")
    if len(parts) < 3:
        raise ValueError(f"Invalid gedq version output: {raw_version!r}")

    try:
        return tuple(int(part) for part in parts[:3])
    except ValueError as exc:
        raise ValueError(f"Invalid gedq version output: {raw_version!r}") from exc


def format_version(version: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in version)


def ensure_gedq_compatible() -> tuple[int, int, int]:
    command = ["gedq", "--version"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"gedq is required at version >= {format_version(REQUIRED_GEDQ_VERSION)}"
        ) from exc

    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise RuntimeError(
            f"gedq is required at version >= {format_version(REQUIRED_GEDQ_VERSION)}; got error: {message}"
        )

    installed_version = parse_version(result.stdout)
    if installed_version < REQUIRED_GEDQ_VERSION:
        raise RuntimeError(
            f"gedq is required at version >= {format_version(REQUIRED_GEDQ_VERSION)}; found {format_version(installed_version)}"
        )

    return installed_version


def load_dataset(gedcom_file: str) -> GedqDataset:
    ensure_gedq_compatible()
    gedcom_path = Path(gedcom_file)

    return GedqDataset(
        individuals=_search_records(gedcom_path, "INDI"),
        families=_search_records(gedcom_path, "FAM"),
        sources=_search_records(gedcom_path, "SOUR", "--expand", "cites"),
        repositories=_search_records(gedcom_path, "REPO"),
    )


def build_sources(records: list[dict]) -> dict[str, Source]:
    sources: dict[str, Source] = {}
    for record in records:
        source = Source()
        source.xref_id = _require_entity_id(record)
        source.title = record.get("title")
        source.author = record.get("author")
        source.publication = _normalize_multiline_text(record.get("publication"))
        source.text = _normalize_multiline_text(record.get("source_text"))
        source.repository_id = record.get("repository_ref")
        sources[source.xref_id] = source
    return sources


def build_repositories(records: list[dict]) -> dict[str, Repository]:
    repositories: dict[str, Repository] = {}
    for record in records:
        repository = Repository()
        repository.xref_id = _require_entity_id(record)
        repository.name = record.get("name") or _first(record.get("name_variants", []))
        repository.www = record.get("www")
        repositories[repository.xref_id] = repository
    return repositories


def build_individuals(records: list[dict], source_records: list[dict]) -> dict[str, Individual]:
    name_source_map = _build_name_source_map(source_records)
    individuals: dict[str, Individual] = {}
    for record in records:
        individual = Individual()
        individual.xref_id = _require_entity_id(record)
        individual.sex = record.get("sex")
        individual.famc_id = record.get("famc")
        individual.fams_ids = _family_ids(record)

        for name in _build_names(record, name_source_map):
            individual.add_name(name)

        for event_record in record.get("events", []):
            event = _build_event(event_record)
            tag = event_record.get("tag")
            if tag in INDIVIDUAL_SINGLE_EVENT_TAGS:
                setattr(individual, INDIVIDUAL_SINGLE_EVENT_TAGS[tag], event)
            elif tag in INDIVIDUAL_MULTI_EVENT_TAGS:
                getattr(individual, INDIVIDUAL_MULTI_EVENT_TAGS[tag])(event)

        for association_record in record.get("associations", []):
            individual.associations.append(_build_association(association_record))

        for source_id in _as_string_list(record.get("source_ids")):
            individual.add_source_id(source_id)

        for note in _build_record_notes(record):
            individual.add_note(note)

        individuals[individual.xref_id] = individual
    return individuals


def build_families(records: list[dict]) -> dict[str, Family]:
    families: dict[str, Family] = {}
    for record in records:
        family = Family()
        family.xref_id = _require_entity_id(record)
        family.husband_id = record.get("husb")
        family.wife_id = record.get("wife")
        family.children_ids = _as_string_list(record.get("chil"))

        for event_record in record.get("events", []):
            tag = event_record.get("tag")
            if tag == "MARR":
                family.marriage = _build_event(event_record)
            elif tag == "RESI":
                family.residences.append(_build_event(event_record))

        for source_id in _as_string_list(record.get("source_ids")):
            family.add_source_id(source_id)

        for note in _build_record_notes(record):
            family.add_note(note)

        families[family.xref_id] = family
    return families


def _search_records(gedcom_path: Path, kind: str, *extra_args: str) -> list[dict]:
    command = [
        "gedq",
        "search",
        str(gedcom_path),
        "--kind",
        kind,
        "--full",
        "--json",
        "--with-src",
        *extra_args,
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise RuntimeError(f"gedq search failed for {kind}: {message}")

    records: list[dict] = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records


def _build_names(
    record: dict,
    name_source_map: dict[tuple[str, str | None], list[str]],
) -> list[Name]:
    occurrences = list(record.get("names", []))
    if occurrences:
        names: list[Name] = []
        for occurrence in occurrences:
            value = occurrence.get("value")
            if not value:
                continue

            name = Name()
            name.value = value

            for source_id in _as_string_list(occurrence.get("source_ids")):
                name.add_source_id(source_id)

            for note in _build_inline_notes(occurrence.get("notes", []), occurrence.get("src")):
                name.add_note(note)

            names.append(name)

        if names:
            return names

    variants = list(record.get("name_variants", []))
    if not variants and record.get("name"):
        variants = [record["name"]]

    names: list[Name] = []
    for variant in variants:
        name = Name()
        name.value = variant
        for source_id in name_source_map.get((_require_entity_id(record), name.value), []):
            name.add_source_id(source_id)
        names.append(name)
    return names


def _build_name_source_map(source_records: list[dict]) -> dict[tuple[str, str | None], list[str]]:
    grouped: dict[tuple[str, str | None], list[str]] = {}
    for source_record in source_records:
        source_id = source_record.get("entity_id")
        if not source_id:
            continue
        for cite in source_record.get("CITES", []):
            if cite.get("subject_kind") != "name":
                continue
            entity_id = cite.get("entity_id")
            if not entity_id:
                continue
            grouped.setdefault((entity_id, cite.get("value")), []).append(source_id)

    return grouped


def _build_event(event_record: dict) -> EventDetail:
    event = EventDetail()
    event.value = event_record.get("value")
    event.date.value = event_record.get("date")
    event.place.value = event_record.get("place")
    event.address = event_record.get("address")
    event.type = event_record.get("type")

    for source_id in event_record.get("source_ids", []):
        event.add_source_id(source_id)

    for note in _build_event_notes(event_record):
        event.add_note(note)

    event.parse_timestamp()
    event.parse_witnesses()
    return event


def _build_association(association_record: dict) -> Association:
    role = association_record.get("role") or ""
    parts = role.split(" ", 1)
    association = Association()
    association.individual_id = association_record.get("target_id")
    association.rel_desc = parts[0] if parts and parts[0] else None
    association.rel_type = parts[1] if len(parts) > 1 else None

    for source_id in association_record.get("source_ids", []):
        association.add_source_id(source_id)

    return association


def _build_record_notes(record: dict) -> list[Note]:
    notes: list[Note] = []

    list_notes = _as_string_list(record.get("NOTE"))
    singular_note = record.get("note")
    if singular_note and not list_notes:
        note = Note()
        note.value = _normalize_multiline_text(singular_note)
        note.line_num = _line_from_source(record.get("src"))
        notes.append(note)

    note_sources = _field_source_list(record.get("field_src"), "NOTE")
    for index, note_value in enumerate(list_notes):
        note = Note()
        note.value = _normalize_multiline_text(note_value)
        note.line_num = _line_from_source(note_sources[index] if index < len(note_sources) else record.get("src"))
        notes.append(note)

    return _dedupe_notes(notes)


def _build_event_notes(event_record: dict) -> list[Note]:
    notes: list[Note] = []
    note_values = list(event_record.get("notes", []))
    note_sources = list(event_record.get("note_src", []))

    for index, note_value in enumerate(note_values):
        note = Note()
        note.value = _normalize_multiline_text(note_value)
        note_source = note_sources[index].get("src") if index < len(note_sources) else event_record.get("src")
        note.line_num = _line_from_source(note_source)
        notes.append(note)

    return notes


def _build_inline_notes(note_values: list[str], source_ref: dict | None) -> list[Note]:
    notes: list[Note] = []
    for note_value in note_values:
        note = Note()
        note.value = _normalize_multiline_text(note_value)
        note.line_num = _line_from_source(source_ref)
        notes.append(note)
    return _dedupe_notes(notes)


def _family_ids(record: dict) -> list[str]:
    famc_id = record.get("famc")
    relations = [relation for relation in record.get("relations", []) if isinstance(relation, str) and relation.startswith("F")]
    return [relation for relation in relations if relation != famc_id]


def _require_entity_id(record: dict) -> str:
    entity_id = record.get("entity_id")
    if not entity_id:
        raise ValueError(f"gedq record has no entity_id: {record}")
    return entity_id


def _line_from_source(source_ref: dict | None) -> int | None:
    if not source_ref:
        return None
    return source_ref.get("line")


def _first(values: list[str]) -> str | None:
    return values[0] if values else None


def _field_source_list(field_src: dict | None, tag: str) -> list[dict]:
    if not field_src:
        return []
    by_tag = field_src.get("by_tag", {})
    value = by_tag.get(tag)
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _normalize_multiline_text(value: str | None) -> str | None:
    if value is None:
        return None
    return value.replace("\r\n", "\n").replace("\n", "\r\n")


def _as_string_list(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _dedupe_notes(notes: list[Note]) -> list[Note]:
    deduped: list[Note] = []
    seen: set[tuple[str | None, int | None]] = set()
    for note in notes:
        key = (note.value, note.line_num)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(note)
    return deduped
