---
slug: improve-performance-birthdays
source: inline-cr
---

# Speed up birthday-index generation with `gedq anniversary --all-days`

## 1. Intent

`gen_site` builds the homepage "born on this day" block from a static index file,
`src/data/birthday-index.json`, emitted by `gen_site/birthday_index.py`. Today that module
calls `gedq anniversary <file> --date "<D> <MON>" --json` **once per calendar day**, looping
all 366 days — 366 `gedq` subprocess launches per site build, which dominates the run.
<!-- from CR:desc "a json page is created by calling gedq anniversary for each day which takes a long time" -->
<!-- observed: gen_site/birthday_index.py:57-104 — _birth_ids_on runs one `gedq anniversary … --date …` per day inside the DAYS_IN_MONTH×day loop -->

`gedq` exposes `anniversary --all-days`, which returns every populated month-day in **one**
invocation. This change replaces the 366-call loop with that single call, producing a
byte-identical index far faster.
<!-- from CR:desc "There is also a command gedq anniversary --all-days which should be used instead to greatly improve the performance of running gen_site" -->
<!-- observed: `gedq anniversary --help` — "--all-days  Return every populated month-day in one invocation; cannot be combined with --date or --today" -->
<!-- observed: one `gedq anniversary Hoofman.ged --date "1 JAN" --json` ≈ 0.52s → ×366 ≈ 192s; one `gedq anniversary Hoofman.ged --all-days --json` ≈ 0.52s (single call), measured 2026-08-06 on gen_site/Hoofman.ged -->

This is a **performance-only, behaviour-preserving** change: the set of people shown on any
day, their order, and the on-disk file are unchanged. Only the mechanism that gathers each
day's birth ids is replaced.

## 2. Functional requirements

**[R-1] Index generation issues exactly one `gedq anniversary … --all-days --json` call, replacing the per-day `--date` loop.**
<!-- from CR:desc "which should be used instead" -->
- AC: A single `build_birthday_index` run invokes `gedq` exactly **once**. That invocation's
  argument vector contains `anniversary`, `--all-days` and `--json`, and does **not** contain
  `--date`. Checkable by intercepting the subprocess call (e.g. patching `subprocess.run`) and
  asserting one call whose args include `--all-days` and exclude `--date`.
- AC: No code path in `gen_site/birthday_index.py` shells out to `gedq anniversary … --date …`
  for index construction after this change; the per-day iteration over `DAYS_IN_MONTH` /
  `MONTH_TAGS` that drove those calls is gone.
  <!-- observed: retirement sweep below — the only `--date` / MONTH_TAGS / DAYS_IN_MONTH / _birth_ids_on sites are gen_site/birthday_index.py and gen_site/test/test_birthday_index.py -->

**[R-2] The generated index is byte-identical to the pre-change per-day output over the same GEDCOM.**
<!-- from CR:desc "greatly improve the performance" (performance-only ⇒ output unchanged) -->
- AC: The `birthday-index.json` produced by the `--all-days` path from `gen_site/Hoofman.ged`
  is **byte-for-byte identical** to the file the current per-day path produces from the same
  GEDCOM. A concrete check: capture the committed index (or regenerate it at the parent commit),
  regenerate with the new code, and `diff` — zero differences.
- AC (grounding — the change is safe to make): across **all 366 calendar days**, the set of
  `BIRT` `entity_id`s returned by `gedq anniversary --all-days` equals, day for day, the set the
  366 per-day `--date` calls return — same populated day keys, no day-level value mismatch. The
  per-day and `--all-days` code paths therefore feed identical ids into the unchanged downstream
  filtering, so the emitted file cannot differ.
  <!-- observed: full-year comparison script over gen_site/Hoofman.ged, 2026-08-06 — "keys only in --all-days: []; keys only in per-day: []; value mismatches on shared keys: []; IDENTICAL BIRT sets across all 366 days: True" -->

**[R-3] The build consumes the `--all-days` payload by its actual shape, not the `--date` shape.**
<!-- from CR:desc "gedq anniversary --all-days … should be used" -->
- AC (literal contract — the two shapes differ): `gedq anniversary … --all-days --json` emits a
  top-level JSON **object keyed by `MM-DD` day strings** (`"01-01"` … `"12-31"`), each value a
  **list of event objects** directly. There is **no** per-day `events` wrapper and **no**
  `query_date` key — those belong to the `--date` shape. Per day, the build selects `entity_id`
  from events where `event == "BIRT"` and `entity_id` is truthy. Verbatim observed samples:
  - `--all-days` day value (the shape to consume): `"01-01": [{"event": "BIRT", "entity_id": "I00091", "name": "N.N. /Walters/", "date": "1 JAN 1864", "day": 1, "month": 1, "year": 1864, "ordinal": 162, "ordinal_kind": "birthday", "lifespan": {"birth": 1864, "death": 1864}, "anchor": {"role": "child", "of": ["I00079", "I00080"], "names": ["Johannes Hubertus /Walters/", "Helena /Blank/"]}}]`
  - `--date` shape (the OLD shape, must NOT be assumed): `{"query_date":"2026-01-01","events":[{"event":"BIRT","entity_id":"I00091", …}]}`
  <!-- observed: `gedq anniversary Hoofman.ged --all-days --json` and `… --date "1 JAN" --json`, 2026-08-06 -->
- AC: The `--all-days` key format `MM-DD` is exactly the index key `birthday_index.py` already
  uses (`day_key(month, day)` → `f"{month:02d}-{day:02d}"`), so a returned key maps to an index
  key with no translation.
  <!-- observed: gen_site/birthday_index.py:52-54 day_key; --all-days keys observed as "01-01"…"12-31" -->

**[R-4] Every downstream filter and structural guarantee is preserved unchanged.**
<!-- from CR:desc "birthday today feature … you see all the birthdays for the current day" (same people, same block) -->
- AC: The ids gathered from `--all-days` still pass through, unchanged, every step that follows
  id-gathering today: (a) the model-membership lookup — an id absent from `model.individuals` is
  skipped; (b) the placeholder/stillbirth name filter (`is_placeholder_name`); (c) the
  oldest-first sort keyed on `(birth_year, xref_id)`; (d) content-only days — a day with no
  surviving candidate gets no key; (e) serialization with `sort_keys=True`, `ensure_ascii=False`,
  `indent=2`, trailing newline.
  <!-- observed: gen_site/birthday_index.py:104-133 (filters + sort) and 143-148 (write) -->
- AC (privacy — protects `[C-1]`): the model-membership skip in (a) is **load-bearing and must
  not be dropped**. `gedq --all-days` reads the raw GEDCOM and has no knowledge of gc2web's
  manual `private: true` exclusion, which is applied only in gc2web's model at parse time; the
  skip is what keeps a `private: true` individual out of the index. It is preserved even though
  no such individual currently has a day-precise birthday — dropping it would be byte-identical
  today yet a latent publication of a withheld person the moment the data gains one.
  <!-- observed: `list_living_private.py` → 0 ids with a day-precise birthday in --all-days output today; by_xref_id built from model.individuals at gen_site/birthday_index.py:99 -->

**[R-5] Index generation still completes without error across the whole year, including 29 February.**
<!-- from CR:desc "for each day … takes a long time" (the loop covered every day; the replacement must too) -->
- AC: A full generation run over `gen_site/Hoofman.ged` exits 0 and raises no error. Because
  `--all-days` returns only populated days and 29 February is unpopulated in this corpus, `02-29`
  is simply absent — no key, no crash — matching the existing content-only behaviour. A non-zero
  `gedq` exit code still surfaces as a raised error rather than a silently empty index.
  <!-- observed: --all-days over Hoofman.ged → 149 populated day keys, no 02-29 key, exit 0 -->

## 3. Technical constraints and decisions

**Locked**

- The replacement uses `gedq anniversary <file> --all-days --json`. The named command is the
  intent, not a builder choice. <!-- from CR:desc -->
- Scope is `gen_site/birthday_index.py` and its test `gen_site/test/test_birthday_index.py`.
  No change to the homepage block, the client-side "today" pick, the index file's name/location/
  format, or `gen_site/gen_site.py`'s call site (its `generate_birthday_index(file, model, path)`
  signature is unchanged). <!-- from CR:desc "Create the spec … improve performance of running gen_site" -->
  <!-- observed: gen_site/gen_site.py:431 calls generate_birthday_index(args.file, GedcomModel(), BIRTHDAY_INDEX_FILE) -->
- `--events` stays at its default (birth only). `--all-days` with the default returns only `BIRT`
  events, matching the current per-day default; no marriage/death events enter the pipeline.
  <!-- observed: --all-days over Hoofman.ged → event types present = {BIRT} only -->

**Delegated — deliberately left to the builder**

- How the loop is restructured: whether to iterate the returned object's keys directly (they are
  already `MM-DD`), whether `_birth_ids_on`, `MONTH_TAGS` and `DAYS_IN_MONTH` are deleted or
  repurposed, and whether a thin per-day accessor is retained. The input fixes the single-call
  mechanism and the byte-identical output, not the internal shape. <!-- from CR:desc -->
- How the test in `gen_site/test/test_birthday_index.py` is updated to survive the symbol/seam
  changes (it currently imports `MONTH_TAGS`/`DAYS_IN_MONTH` and patches `_birth_ids_on`). Note:
  that test independently computes its expected index via per-day `--date` calls — keeping that
  per-day oracle while production switches to `--all-days` turns the test into a direct
  equivalence proof, but whether to do so is the builder's call.
  <!-- observed: gen_site/test/test_birthday_index.py:31-32 imports, 51-64 per-day fixture, 239 patch of _birth_ids_on -->

## 4. Invariants and edge cases

- `--all-days` "cannot be combined with `--date` or `--today`" — the single call carries no date
  argument. <!-- observed: `gedq anniversary --help` -->
- Intra-day input order is irrelevant to the output: candidates are sorted on `(birth_year,
  xref_id)` before writing and day keys are emitted with `sort_keys=True`, so even if `--all-days`
  orders a day's events differently from the per-day call, the written file is unchanged.
  <!-- observed: gen_site/birthday_index.py:129-131 sort + :145 sort_keys=True -->
- Dependency-drift risk (carried from the existing feature, unchanged by this CR): the set of
  dates `gedq` treats as deterministic is `gedq`'s call, not gc2web's. This change does not alter
  that contract — it only swaps 366 queries of it for one. If a future `gedq` release changes
  which births are deterministic, both the old and new paths would move together.
  <!-- observed: gen_site/birthday_index.py module docstring — "Date determinism — gedq's call, not ours" -->
- `gen_site/Hoofman.ged` currently yields 149 populated day keys via `--all-days`; this figure
  rots with the data and is not part of any acceptance bar — [R-2]'s byte-identical check and the
  366-day equivalence are the durable contract. <!-- observed: --all-days over Hoofman.ged, 2026-08-06 -->

**Retirement sweep** — the mechanism being retired is the per-day
`gedq anniversary … --date … --json` call and the loop scaffolding that drove it. Sweep derived
from what the change forbids (per-day `--date` iteration for the index), not from the old wording:

- `grep -rn '\-\-date\|MONTH_TAGS\|DAYS_IN_MONTH\|_birth_ids_on\|anniversary' gen_site --include=*.py`
  and `grep -rn 'get("events"' gen_site --include=*.py`.
- Statement sites (both must be updated): **`gen_site/birthday_index.py`** — module docstring
  line 13, `MONTH_TAGS` (35), `DAYS_IN_MONTH` (39), `_birth_ids_on` (57–76, incl. `--date` at 64
  and `payload.get("events", [])` at 76), the `enumerate(DAYS_IN_MONTH)` / `range(day)` loop
  (100–104). **`gen_site/test/test_birthday_index.py`** — imports of `MONTH_TAGS`/`DAYS_IN_MONTH`
  (31–32), the per-day `--date` fixture builder (51–64), and the `patch("birthday_index._birth_ids_on")`
  (239).
- **Not sites** (same `events` token, different payload): `gen_site/adapter/gedq_adapter.py:133,163`
  and `gen_site/test/test_migration_contract.py:124-166` read `record.get("events", …)` on gedq's
  entity/record dump, not the `anniversary` payload.
  <!-- observed: grep sweep over gen_site/, 2026-08-06 -->

## 5. Scope fence — non-goals

- No change to what the birthday block shows, its Dutch wording, ordering, or empty-state — this
  is performance-only. The behavioural contract stays owned by
  `specs/birthday-today/birthday-today.cr.md`. <!-- from CR:desc -->
- No change to the index file's name, location, or serialization format. <!-- from CR:desc -->
- No caching layer, no `--cache-dir` use, no persisted derived artifact — the single call is the
  whole optimization. <!-- from CR:desc (only --all-days named) -->
- No change to gedq itself, its determinism filter, or the vendored gedq version.
  <!-- from CR:desc -->
- No revision of `birthday-today.cr.md` or the constitution; this CR is a separate artifact.

## Constitution Mapping

Source: `specs/constitution.md` (governing — no `constitution_scope` declaration). Classified via
`create-constitution/scripts/constitution-ci.py --list`:

- `[C-1]` → **RUNNABLE** → **runner-enforced**, not mapped. Its `Check:`
  (`bash -c 'cd gen_site && env -u VIRTUAL_ENV uv run python -m pytest test/test_migration_contract.py -k test_private_people_are_excluded'`)
  is run by the constitution CI runner at build (build-cr) and in create-review's executed lane on
  every change, so enumerating it per-CR would be redundant. (Its privacy intent is nonetheless
  honoured concretely by [R-4]'s model-membership-skip AC.)

Constitution mapping: 1 non-advisory sub-clause = 0 mapped (runner won't run — REVIEWER/UNSUPPORTED; 0 applies, 0 not-applicable, 0 = 0 + 0) + 1 runner-enforced (RUNNABLE/PARTIAL, not mapped).
