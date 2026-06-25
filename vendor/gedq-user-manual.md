# gedq User Manual

This manual starts with first-use commands and builds toward scripting, guarded edits, and raw graph queries. All examples use real commands supported by the current CLI.

## What gedq Does

`gedq` reads, searches, validates, and edits GEDCOM files.

At a high level, you can use it to:

- inspect one person, family, or source record
- search across a file by name, place, date, occupation, text, and related filters
- walk family relationships such as ancestors, descendants, siblings, and kinship paths
- render deterministic ASCII trees, anniversary reports, and aggregate reports when you need a compact overview
- validate data quality issues without blocking normal reads
- make guarded file edits with atomic writes
- run raw Cypher queries against the derived graph when you need more than the high-level commands

## Who This Manual Is For

- If you are new to GEDCOM command-line tools, start with the beginner sections and run the examples exactly as shown.
- If you already know your way around genealogical data, jump to the search, relationship, and write sections.
- If you want to automate gedq or use its graph model directly, read the JSON and raw query sections near the end.

## Example File Used in This Manual

Most examples below use a generic file name:

```bash
data.ged
```

For write examples, make a disposable copy first so you do not edit your main file in place:

```bash
cp data.ged working-data.ged
```

## First Run

Run the CLI directly as `gedq`:

```bash
gedq --help
```

You can also ask for the version:

```bash
gedq --version
```

The top-level commands are:

- `person`
- `family`
- `source`
- `search`
- `ancestors`
- `descendants`
- `siblings`
- `path`
- `tree`
- `analyze`
- `anniversary`
- `query`
- `schema`
- `validate`
- `add`
- `edit`
- `delete`

## Output Modes

Before using the commands, understand one important default:

- when output goes to a terminal, gedq defaults to human-readable output
- when output is piped or redirected, gedq defaults to JSON output

You can always override that with:

- `--human`
- `--json`

For JSON output, you can also control density:

- default JSON uses the lean / compact read shape
- default JSON also **omits file/line provenance** (`src`, `field_src`, `note_src`); pass `--with-src` to include it
- `--verbose-json` keeps compatibility fields for consumers that expect explicit empty or null entries
- `--collapse-place` deduplicates repeated identical place strings within one response

Examples:

```bash
gedq person I00002 data.ged
gedq person I00002 data.ged --human
gedq person I00002 data.ged --json
gedq search data.ged --surname Hoofman > results.jsonl
```

## Beginner: Read One Record

### Look Up One Person

The most common first command is `person`:

```bash
gedq person I00002 data.ged
```

That looks up the person record with identifier `I00002`.

To force JSON:

```bash
gedq person I00002 data.ged --json
```

For people with repeated GEDCOM `NAME` structures, JSON exposes two related name surfaces:

- `name_variants` is the summary list of raw `NAME` strings in source order
- `names` is the canonical per-occurrence projection, one object per GEDCOM `NAME`, carrying its own `name_index`, `value`, direct `source_ids`, attached `notes`, derived `note_refs`, and `src` when `--with-src` is used

Use `names` when you need first-class repeated-name identity, such as preserving name-attached notes or keeping source grouping stable across repeated `NAME` occurrences.

Typical uses:

```bash
gedq person I1 data.ged --json
gedq person I00001 data.ged --human
gedq person I99999 data.ged --json
```

Notes:

- a missing record returns a JSON error envelope and exit code 1 in JSON mode
- a missing record prints `entity not found: <ID>` and exits with code 1 in human mode

### Show More Detail

Human mode supports three useful views.

Compact view is the default:

```bash
gedq person I00002 data.ged --human
```

Full view shows more fields and event details:

```bash
gedq person I00002 data.ged --human --full
```

Narrative view turns the record into prose:

```bash
gedq person I00002 data.ged --human --narrative
```

The same pattern works for `family` and `source`.

### Look Up One Family

```bash
gedq family F00001 data.ged --json
gedq family F00001 data.ged --human --full
gedq family F00001 data.ged --table
```

Family records are useful when you want to inspect spouses and children directly.

`--table` is useful for dense side-by-side inspection. It prints deterministic columns for `id`, `name`, `birth`, and `death` with parents shown first, followed by children.

### Look Up One Source

```bash
gedq source S00001 data.ged --json
gedq source S00001 data.ged --human --full
gedq source S00001 data.ged --json --expand REPO
gedq source S00096 data.ged --json --expand cites
```

If a source record carries linked repository-style references, `--expand` inlines them the same way lookup expansion works on people and families. The expand selector stays GEDCOM-tag-oriented (`REPO`), but the emitted JSON still uses the canonical outward key names such as `repository_ref`. Source lookups also support synthetic `CITES` expansion, which inlines resolved citation-fact rows for that source under `CITES`, **plus a sibling `EVENT_NOTES` array** holding the witnesses and time-of-day notes on each cited event (one row per note-bearing event, with `owner_id`, `owner_kind`, `event_tag`, `event_source_ids`, `notes`, and `note_refs`). The note layer is not a citation edge, so it rides alongside `CITES` rather than inside it.

## Beginner: Expand Linked References

Use `--expand` to inline additional payload for a selected GEDCOM reference tag, event tag, or source-only selector.

- for record-style commands such as `person`, `family`, `source`, and `search`, pass one or more selectors such as `FAMC`, `FAMS`, `HUSB`, `WIFE`, `REPO`, `OCCU`, `MARR`, or source-only `CITES`
- use `--expand all` when you want every supported expansion in that payload
- for traversal commands such as `ancestors`, `descendants`, `siblings`, and `path`, only `--expand all` is supported

Examples:

```bash
gedq person I00001 data.ged --json --expand FAMC
gedq family F00001 data.ged --json --expand HUSB
gedq family F00001 data.ged --json --expand MARR
gedq source S00001 data.ged --json --expand REPO
gedq source S00096 data.ged --json --expand cites
gedq search data.ged --surname Hoofman --json --expand FAMC
gedq person I00002 data.ged --json --expand FAMS
gedq person I00077 data.ged --json --expand OCCU
gedq ancestors I00001 data.ged --json --expand all
gedq path I00001 I00004 data.ged --json --expand all
```

What this is good for:

- `person --expand FAMC` lets you inspect the family where the person is a child
- `person --expand FAMS` lets you inspect the family where the person is a spouse
- `person --json` plus the `names` array lets you inspect one object per repeated GEDCOM `NAME`, including per-name citations, `NAME`-attached notes, and provenance when requested
- `family --expand HUSB` or `family --expand WIFE` lets you inspect linked people without a second command
- `family --expand MARR` lets you inspect a family event inline without reading the full `events` list
- `source --expand REPO` lets you inspect linked repository-style references when they exist
- `source --expand cites` returns compact cited-fact rows (`CITES`) plus the cited events' notes (`EVENT_NOTES`), often cheaper than `search --cites` when you need citation subjects rather than full citing records
- `search --expand ...` lets one discovery step return enriched payloads instead of only compact hits
- `person --expand OCCU` returns occupation events inline, including available event details
- traversal commands use `--expand all` to inline linked lookup payloads inside typed traversal elements

If a requested reference is dangling or missing, the expanded field is returned as `null` in JSON mode.

For event-tag expansion:

- no matching events means the expanded value is `null`
- one matching event returns a single object
- multiple matching events return a list of objects

## Beginner: Discover the Output Schema

Use `schema` when you want machine-readable contracts for output payloads.
The command is output-contract-only and does not read a GED file.

Examples:

```bash
gedq schema --mode person
gedq schema --mode family
gedq schema --mode source
gedq schema --mode event
gedq schema --mode note
```

Common uses:

- generate parser contracts for scripts and pipelines
- inspect which event fields are available before writing automation
- inspect the standalone event and note payload contracts used inside larger responses
- validate downstream assumptions during upgrades

## Beginner: Search a GEDCOM File

The `search` command is the fastest way to answer questions like:

- Who has this surname?
- Who was born around this year?
- Who appears in this place?
- Which records cite a specific source?

Basic examples:

```bash
gedq search data.ged --surname Hoofman --json
gedq search data.ged --name Petrus --human
gedq search data.ged --place Rotterdam --json
```

You can combine filters:

```bash
gedq search data.ged --surname Hoofman --year 1965 --json
gedq search data.ged --name Kid --occupation Carpenter --year-from 1965 --year-to 1965 --json
gedq search data.ged --place Rotterdam --year 1965 --human --full
```

Useful filters:

- `--surname`
- `--name`
- `--place`
- `--year`
- `--year-from`
- `--year-to`
- `--occupation`
- `--residence`
- `--sex`
- `--text`
- `--kind`
- `--cites`

More examples:

```bash
gedq search data.ged --sex F --json
gedq search data.ged --kind INDI --surname Hoofman --json
gedq search data.ged --cites S00001 --json
gedq search data.ged --text Hoofman --json
gedq search data.ged --residence Rotterdam --json
```

### Understanding Search Output

`search` returns multiple records, so JSON mode uses JSON Lines rather than one big JSON array. That means you get one JSON object per line.

By default each match is a **lean row** — `entity_id`, `kind`, `name`, primary date, and place — which is what you usually need to rank candidates. Pass `--full` to return the complete record per match (every event and source); `--full` also drives the fuller human-readable view.

Example:

```bash
gedq search data.ged --surname Hoofman --json
```

This is especially convenient for shell pipelines and log-style processing.

## Intermediate: Relationship Commands

Once you can read records and search, the next step is relationship traversal.

### Ancestors

```bash
gedq ancestors I00001 data.ged --json
gedq ancestors I00001 data.ged --json --depth 1
gedq ancestors I00001 data.ged --human
```

Use `--depth` when you want a bounded traversal.

### Descendants

```bash
gedq descendants I00002 data.ged --json
gedq descendants I00002 data.ged --human
gedq descendants I00002 data.ged --json --depth 2
```

### Siblings

```bash
gedq siblings I00001 data.ged --json
gedq siblings I00001 data.ged --human
```

### Path Between Two People

`path` shows the shortest relationship path between two IDs.

```bash
gedq path I00001 I00004 data.ged --json
gedq path I00001 I00004 data.ged --human
```

Advanced path modes:

```bash
gedq path I00001 I00004 data.ged --json --common-ancestor
gedq path I00001 I00004 data.ged --json --cousin-distance
```

Rules:

- use at most one of `--common-ancestor` and `--cousin-distance`
- if you pass both, the command exits with a user error

### Cycle Notices

If your data contains a cyclic pedigree, gedq does not loop forever. Instead it returns the visited IDs plus a notice.

Example:

```bash
gedq ancestors I1 data.ged --json
gedq descendants I1 data.ged --json
```

In JSON mode, the result contains:

- `elements`
- `notices`

Traversal person elements use `entity_id`, not `id`, so one jq path such as `.elements[] | select(.type=="person") | .entity_id` works across `ancestors`, `descendants`, `siblings`, and `path`.

## Intermediate: On This Day Reports

`anniversary` answers the day-specific question "which recorded events fall on this calendar day?"

Examples:

```bash
gedq anniversary data.ged --human
gedq anniversary data.ged --json
gedq anniversary data.ged --date 2026-06-23 --json
gedq anniversary data.ged --date '23 JUN' --events birth,marriage,death --human
```

Important defaults:

- if you omit `--date`, gedq uses today
- `--today` is the explicit form of that same default and cannot be combined with `--date`
- if you omit `--events`, only birthdays are reported
- `--events` accepts a comma-separated subset of `birth`, `marriage`, and `death`

Matching rules:

- matching is by day and month, not by year
- `--date` accepts either `YYYY-MM-DD` or `DD MON`
- exact dates such as `15 JUL 1899` match, but approximate or partial dates such as `ABT 15 JUL 1899`, `BEF 23 JUN`, or year-only dates do not
- Feb 29 only matches on Feb 29; gedq does not silently shift leap-day anniversaries to Feb 28 or Mar 1

Human output prints one line per event with the event tag, the identifying person or spouse pair, the owning GEDCOM ID, the original event date, and an anniversary-style ordinal when the year is known.

JSON output returns a stable envelope:

```json
{"query_date":"2026-06-23","events":[...]}
```

If no records match, human mode prints a single "no anniversaries" line and JSON mode returns an empty `events` array.

## Intermediate: Validate Data Quality

`validate` is for data quality checks that should be reported explicitly rather than silently blocking normal reads.

Examples:

```bash
gedq validate data.ged --json
gedq validate data.ged --human
gedq validate data.ged --json
```

Typical issues include:

- blank values
- dangling references
- dangling references extracted from event NOTE text (`note_refs`)
- missing required tags
- cyclic pedigrees

### Scope and Compare Validation Output

By default `validate` reports every issue in the file. You can narrow it:

```bash
gedq validate data.ged --json --entity I00021             # only issues on one record (repeat --entity to union)
gedq validate data.ged --json --code duplicate-citation   # only one issue code (repeat --code to union)
```

To answer "did my recent edit introduce a problem?", compare against a baseline snapshot:

```bash
gedq validate data.ged --json --baseline pre-edit.json                    # first run creates the snapshot (0 new); later runs report only findings NEW since it
gedq validate data.ged --json --baseline pre-edit.json --update-baseline  # rewrite the snapshot to the current set
```

The baseline is **stable**: a plain `--baseline` read does not modify the file, so "new since baseline" survives a whole edit-and-fix cycle; only `--update-baseline` moves it. The diff keys on a stable signature (code + entity + field-path), not line numbers, so an edit that merely shifts line positions does not show up as new.

Important behavior:

- a normal lookup may still succeed even if `validate` reports issues
- this lets you inspect imperfect data and then decide whether to clean it up

Example workflow:

```bash
gedq person I1 data.ged --json
gedq validate data.ged --json
```

The first command reads the record. The second command surfaces the data quality findings.

## Intermediate: Understand Errors

gedq distinguishes between user-facing usage problems and data or parse failures.

Examples:

```bash
gedq person
gedq stats
gedq person I1 data.ged --human
gedq person I1 data.ged --json
```

What to expect:

- missing arguments and unknown commands fail cleanly without a traceback
- human-mode parse failures are written as plain error text
- JSON-mode failures return a structured error envelope

This matters when you automate the tool and need machine-readable failures.

## Intermediate: Safe Write Workflow

Before editing a GEDCOM file, understand the write safety model.

gedq uses guarded, file-first writes:

- it reads the file
- it checks cached metadata for the last known snapshot
- it writes atomically
- it rejects stale writes if the file changed externally since your last read

In practice, do this:

```bash
cp data.ged working-data.ged
gedq person I00002 working-data.ged --json
```

Then perform your edit.

If the file changes externally after your read, you may see:

```text
file modified externally, reload first
```

When that happens, run another read command first, then retry the edit.

## Advanced: Add Records

The `add` command creates a new top-level GEDCOM record.

Basic form:

```bash
gedq add person working-data.ged --set 'name=New /Person/' --set 'sex=F'
```

Preview the guarded write plan without mutating the file:

```bash
gedq add person working-data.ged --set 'name=New /Person/' --set 'sex=F' --dry-run
```

If you omit `--id`, gedq generates the next ID for that record family.

You can also choose the ID explicitly:

```bash
gedq add person working-data.ged --id I90000 --set 'name=Probe /Person/'
```

`gedq add --help` and unsupported-kind errors advertise this canonical kind set:

- `person`
- `family`
- `source`
- `note`
- `repo`
- `object`
- `submitter`

Accepted aliases still normalize internally on the command line: `indi`, `fam`, `sour`, `obje`, and `subm`.

### Add Examples

Add a person:

```bash
gedq add person working-data.ged --set 'name=Child /One/' --set 'sex=F'
```

Add a family:

```bash
gedq add family working-data.ged --set 'husb=I00001' --set 'wife=I00004' --add 'chil=I00010'
```

Add a source:

```bash
gedq add source working-data.ged --set 'text=City archive ledger'
```

Create one value-bearing event with nested children on the `add` path:

```bash
gedq add person working-data.ged --set 'name=T /X/' --add 'OCCU=Bakker' --add 'OCCU.SOUR=@S0001@'
```

That creates one `OCCU` structure whose line value is `Bakker` and whose nested `SOUR` points at `@S0001@`.

The command prints the created ID on success.

## Advanced: Edit Records

The `edit` command supports four mutation styles:

- `--set field=value`
- `--add field=value`
- `--clear field`
- `--remove field=value`

You can preview the guarded write plan first:

```bash
gedq edit I00002 working-data.ged --set 'name=Petrus Johannes /Hoofman/' --dry-run
```

### Top-Level Field Edits

Examples:

```bash
gedq edit I00002 working-data.ged --set 'name=Petrus Johannes /Hoofman/'
gedq edit I00002 working-data.ged --add 'note=Research note from city archive'
gedq edit I00002 working-data.ged --clear note
gedq edit I00002 working-data.ged --remove 'fams=F00003'
```

### Event Field Edits with Dot Notation

Event fields use dotted syntax such as `birt.date` and `birt.place`.

Examples:

```bash
gedq edit I00002 working-data.ged --set 'birt.date=30 JUN 1965'
gedq edit I00002 working-data.ged --set 'birt.place=Rotterdam'
gedq edit I00002 working-data.ged --set 'birt.addr=Madernestraat'
gedq edit I00002 working-data.ged --add 'birt.sour=S1'
```

One common pattern is to update multiple parts of the same event in one command:

```bash
gedq edit I00002 working-data.ged \
  --set 'name=Child /Updated/' \
  --set 'birt.date=30 JUN 1965' \
  --set 'birt.place=Rotterdam'
```

### Addressing One of Several Same-Tag Structures

When a record has more than one structure of the same tag — multiple `FACT`s, or multiple `SOUR` citations on one event — address a specific one with a **1-based index**:

```bash
gedq edit I00021 working-data.ged --set 'FACT[2].TYPE=Buitenechtelijk'   # the 2nd FACT
gedq edit I00021 working-data.ged --add 'birt[1].sour=S38'               # add a 2nd citation to the 1st BIRT
gedq edit I00021 working-data.ged --clear 'FACT[3]'                       # delete the 3rd FACT
```

Rules:

- a **bare** `--add 'FACT.TYPE=…'` (no index) always **creates a new** structure; grouped sub-fields in one command land on that single new one
- a bare `--set`, `--clear`, or `--remove` on a tag that has **two or more** siblings **errors** and asks for an index, rather than silently changing the first
- multiple indexed operations in one command resolve against **pre-edit** order, so `--clear 'FACT[1]' --clear 'FACT[3]'` removes the original 1st and 3rd (not a renumbered target)
- alias sub-fields (`date`, `place`, `sour`, `addr`, …) are lowercase and case-insensitive; a raw GEDCOM tag with no alias — notably a `FACT`/`EVEN` `TYPE` — is written as the **uppercase** tag (`FACT[2].TYPE`, not `fact[2].type`)
- a bare child add such as `--add 'DEAT.NOTE=...'` can legitimately create a second `DEAT`; if that new sibling would still have no line value, `DATE`, or `PLAC`, gedq keeps the write valid but emits an advisory warning in both `--dry-run` output and live apply output, and points you to an indexed target such as `DEAT[2].NOTE`
- to **overwrite a multi-line `NOTE` in place** rather than append another, address it by index and use `--set` — `--set 'BIRT[1].NOTE[2]=<entire new note value>'` replaces that note's whole content, leaving the note count unchanged. `--clear 'BIRT[1].NOTE[2]'` deletes just that one note, and `--remove 'BIRT[1].NOTE=<exact existing value>'` removes the note whose multi-line value matches. `--add 'BIRT.NOTE=…'` always **appends a new** note, so use `--set` (not `--add`) when amending an existing one — e.g. adding a field to a witness already listed in a witnesses note

Aliases you can use include:

- `name`
- `sex`
- `note`
- `text`
- `title`
- `husb`
- `wife`
- `chil`
- `famc`
- `fams`
- `place`
- `date`
- `address` or `addr`
- `occupation`
- `source` or `sour`
- `source_text` (the `--json` transcript key — routes to the `TEXT` tag)
- `cause` (event-dotted, e.g. `deat.cause` — routes to `CAUS`)
- `nickname` (routes to the `NAME.NICK` name piece)

The descriptive forms above (`source_text`, `cause`, `nickname`) are the same keys `gedq <kind> --json` emits, so a value you read can be fed straight back as a `--set`/`--add` token — read and write share one vocabulary. The **structural / aggregate** read keys — `value`, `media_path`, `source_ids`, `notes`, `note_refs`, `associations` — are *not* directly writable; setting one returns a **targeted** error naming the correct write path (e.g. `value` → write the event's own tag, such as `OCCU=…`; `media_path` → `FILE=…` on the linked OBJE record; `source_ids` → `SOUR=…`).

Supported event groups include:

- `birt`
- `deat`
- `resi`
- `occu`
- `marr`
- `marb`
- `fact` (an attested fact; its label is the raw `TYPE` tag — see the same-tag-structures note above)
- `even` (a generic event; its label is also the raw `TYPE` tag)

### Verifying an Edit

After any write, read the record back immediately:

```bash
gedq person I00002 working-data.ged --json
gedq search working-data.ged --place Rotterdam --year 1965 --json
```

That gives you a cheap confirmation that the mutation landed where you expected.

**Read keys can differ from the tag you wrote.** `--json` renames some fields in its output — most notably the transcript tag `TEXT` reads back as **`source_text`** (likewise `FILE`→`media_path`, `NICK`→`nickname`). When confirming such a write, check the *read* key (`source_text`), not the tag name (`TEXT`) — otherwise a successful write looks empty (`0 chars`). Those same descriptive keys are accepted back as `--set`/`--add` tokens (see the alias list above), so a read value round-trips on write.

## Advanced: Delete Records

Delete removes one top-level entity by ID.

By default, delete is guarded: if other records still point at the target, gedq blocks the delete and reports the inbound references. Use `--cascade` only when you want gedq to remove those inbound pointers as part of the same operation.

```bash
gedq delete I90000 working-data.ged
gedq delete I90000 working-data.ged --json
gedq delete I90000 working-data.ged --dry-run
gedq delete I90000 working-data.ged --cascade --dry-run
```

A safe delete workflow looks like this:

```bash
gedq person I90000 working-data.ged --json
gedq delete I90000 working-data.ged
gedq person I90000 working-data.ged --json
```

After deletion, the final lookup should fail with the standard JSON error envelope in JSON mode.

If delete reports inbound references, inspect them first, then preview the cleanup plan:

```bash
gedq delete I90000 working-data.ged --cascade --dry-run
```

## Advanced: JSON for Automation

If you are scripting gedq, prefer explicit `--json` even when redirection would trigger JSON automatically. That makes your scripts easier to read and less sensitive to environment changes.

If your automation expects stable key presence, choose one JSON policy explicitly:

- default compact JSON (smaller payloads)
- `--verbose-json` for compatibility with consumers that expect explicit empty/null fields
- file/line provenance (`src`/`field_src`/`note_src`) is omitted by default; add `--with-src` if your tooling needs locations

Examples:

```bash
gedq person I00002 data.ged --json > /tmp/person.json
gedq person I00002 data.ged --json --verbose-json > /tmp/person-verbose.json
gedq person I00077 data.ged --json --collapse-place > /tmp/person-collapsed.json
gedq family F00001 data.ged --json > /tmp/family.json
gedq validate data.ged --json > /tmp/issues.json
gedq search data.ged --surname Hoofman --json > /tmp/search.jsonl
```

Things to remember:

- single-record lookups return a single JSON object on success
- `search` and multi-row `query` return JSON Lines
- traversal commands return a stable JSON object with `elements` and `notices`
- traversal person elements are keyed by `entity_id`
- some graph commands return JSON objects with named fields such as `common_ancestor` or `cousin_distance`
- parse and user errors also have a JSON form when `--json` is active

Value-bearing event and attribute fields such as `OCCU` read back through one logical `value` even when GEDCOM stores them across `CONC` continuation lines on disk.

## Advanced: Raw Cypher Queries

Use `query` when the high-level commands are not enough.

Basic example:

```bash
gedq query "MATCH (e:entities) RETURN e.id AS id ORDER BY id;" data.ged --json
```

Discover the built-in query catalog:

```bash
gedq query --examples
gedq query --examples --markdown
```

Find one record directly:

```bash
gedq query "MATCH (e:entities {id: 'I2'}) RETURN e.id AS id;" data.ged --json
```

Match a record by its own fields. Entity nodes carry `id`, `kind`, and the documented scalar `entity_properties` surface from `query --examples`: `media_path`, `media_form`, `media_title`, `name`, `nickname`, `sex`, `husb`, `wife`, `abbr`, `auth`, `title`, `publication`, and `repository_ref`. Event nodes carry `owner_id`, `tag`, `date_raw`, `year`, and `place`. So you can filter on a record's metadata:

```bash
gedq query "MATCH (s:entities {kind:'SOUR'}) WHERE s.publication CONTAINS '<handle-uuid>' RETURN s.id AS id;" data.ged --json
gedq query "MATCH (s:entities {kind:'SOUR'}) WHERE s.title CONTAINS 'Hoofman' RETURN s.id AS id, s.title AS title;" data.ged --json
```

Compatibility aliases such as `s.PUBL`, `s.TITL`, and `n.SEX` are still accepted on the query side, but the canonical documented names are the descriptive forms above. Not every outward JSON field is a node property: event-payload text (an OCCU event's `value`, note bodies), structural aggregates such as `media_refs`, and the transcript (`source_text` / GEDCOM `TEXT`) are kept off the nodes, so `RETURN s.source_text` fails with `Binder exception`. Run `query --examples` for the authoritative `entity_properties` / `event_properties` lists.

Use cases:

- custom reports not covered by `search`
- debugging the derived graph
- experimentation before proposing a new dedicated CLI command

Recommendations:

- start with a read-only query that returns IDs and a small number of fields
- keep shell quoting simple by wrapping the whole Cypher statement in double quotes
- use `--examples` when you need a supported starting point instead of writing Cypher from scratch
- `--markdown` only works together with `--examples`
- prefer a dedicated top-level command when your workflow becomes repeatable for non-experts

## Practical Workflows

### Workflow 1: Find One Person and Inspect Their Family

```bash
gedq search data.ged --surname Hoofman --json
gedq person I00001 data.ged --human --full
gedq person I00001 data.ged --json --expand FAMC
```

### Workflow 2: Investigate a Place and Year

```bash
gedq search data.ged --place Rotterdam --year 1965 --json
gedq search data.ged --place Rotterdam --year-from 1960 --year-to 1970 --human
```

### Workflow 3: Confirm a Relationship Claim

```bash
gedq path I00001 I00004 data.ged --json
gedq path I00001 I00004 data.ged --json --common-ancestor
gedq path I00001 I00004 data.ged --json --cousin-distance
```

### Workflow 4: Add, Verify, and Remove a Test Record

```bash
cp data.ged working-data.ged
gedq person I00002 working-data.ged --json
gedq add person working-data.ged --id I90000 --set 'name=Integration /Probe/' --set 'sex=F'
gedq search working-data.ged --surname Probe --json
gedq delete I90000 working-data.ged
```

### Workflow 5: Validate Before Shipping a File

```bash
gedq validate working-data.ged --human
gedq validate working-data.ged --json
```

The human form is easier to read. The JSON form is better for tooling and CI-style checks.

## Troubleshooting

### I got `not found`

Check the ID and the file path first.

Examples:

```bash
gedq person I00002 data.ged --json
gedq family F00001 data.ged --json
```

### I got `file modified externally, reload first`

Run any read command on the file and retry the mutation:

```bash
gedq person I00002 working-data.ged --json
gedq edit I00002 working-data.ged --set 'note=Fresh retry after reload'
```

### My script expected JSON but got human text

Add `--json` explicitly:

```bash
gedq search data.ged --surname Hoofman --json
```

### The first read or search seemed to hang

On the first query against a GEDCOM file, gedq builds a derived cache beside the source file:

```text
data.ged.ladybug/
```

That first build can take noticeably longer on larger files. Later commands reuse the cache and should be much faster unless the GEDCOM file changed and gedq needs to rebuild it.

### A malformed date caused a failure

Example:

```bash
gedq person I1 data.ged --json
```

In this case the parser is rejecting unsupported date syntax. Fix the GEDCOM value and rerun the command.

### I passed both `--common-ancestor` and `--cousin-distance`

Choose one mode only:

```bash
gedq path I00001 I00004 data.ged --json --common-ancestor
gedq path I00001 I00004 data.ged --json --cousin-distance
```

## Command Cheat Sheet

```bash
gedq person ID data.ged [--full] [--with-src]
gedq family ID data.ged [--full] [--with-src] [--table]
gedq source ID data.ged [--expand TAG[,TAG...]|all] [--with-src]
gedq search data.ged [filters] [--full] [--with-src] [--expand TAG[,TAG...]|all]
gedq ancestors ID data.ged [--depth N] [--expand all]
gedq descendants ID data.ged [--depth N] [--expand all]
gedq siblings ID data.ged [--expand all]
gedq path LEFT_ID RIGHT_ID data.ged [--common-ancestor|--cousin-distance] [--expand all]
gedq tree ID data.ged --direction up|down [--depth N] [--mode clean|annotated]
gedq analyze data.ged [--report census,coverage,structure,duplicates] [--json|--human]
gedq anniversary data.ged [--date YYYY-MM-DD|'DD MON'|--today] [--events birth[,marriage,death]] [--json|--human]
gedq schema --mode person|family|source|event|note
gedq validate data.ged [--entity ID] [--code CODE] [--baseline FILE] [--update-baseline]
gedq add KIND data.ged [--set field=value] [--add field=value] [--dry-run]
gedq edit ID data.ged [--set field[i]=value] [--add field=value] [--clear field[i]] [--remove field[i]=value] [--dry-run]
gedq delete ID data.ged [--cascade] [--dry-run]
gedq query --examples [--markdown]
gedq query "MATCH ..." data.ged [--json|--human]
```

## Where to Start Next

- If you are new, practice with `person`, `search`, and `validate` first.
- If you are doing family analysis, learn `ancestors`, `descendants`, `siblings`, and `path` together.
- If you are maintaining files, use a copy, read before you write, and verify every mutation with a follow-up lookup.
- If you are building tooling around gedq, standardize on explicit `--json` and treat `search` and multi-row `query` as JSONL producers.
