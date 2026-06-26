import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from model.GedcomModel import GedcomModel


WORKSPACE_DIR = Path("/workspace")
GEN_SITE_DIR = WORKSPACE_DIR / "gen_site"
CONTENT_DIR = WORKSPACE_DIR / "src/content/entity"
GEDCOM_FILE = GEN_SITE_DIR / "Hoofman.ged"
BASELINE_COMMIT = "eab4d3063c936fb1ba79878d24cda21b95bd5f21"
ALLOWLIST_FILE = GEN_SITE_DIR / "test/migration_allowlist.json"
TREE_SECTION_RE = re.compile(r"### Boom\n.*?(?=\n### |\Z)", re.DOTALL)
ASCII_TREE_BLOCK_RE = re.compile(r'<div class="ascii-tree-wrap">.*?</div>', re.DOTALL)
FRONTMATTER_METADATA_RE = re.compile(
    r'^(lifespan|birth_place|death_place|relationship_summary|branch): .*\n?',
    re.MULTILINE,
)
SECTION_ORDER_RE = re.compile(r'^section_order:\n(?:  - .*\n)+', re.MULTILINE)


def run_command(*command: str, cwd: Path = WORKSPACE_DIR) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    python_path = env.get("PYTHONPATH")
    env["PYTHONPATH"] = "." if cwd == GEN_SITE_DIR and not python_path else f".:{python_path}" if cwd == GEN_SITE_DIR else python_path or ""
    return subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, check=True)


def load_jsonl_output(kind: str) -> list[dict]:
    result = run_command(
        "gedq",
        "search",
        str(GEDCOM_FILE),
        "--kind",
        kind,
        "--full",
        "--json",
        "--with-src",
        cwd=WORKSPACE_DIR,
    )
    return [json.loads(line) for line in result.stdout.splitlines() if line.strip()]


def schema_project(record: dict, allowed_keys: set[str]) -> dict:
    return {key: value for key, value in record.items() if key in allowed_keys}


def normalize_tree_section(page_text: str) -> str:
    text = TREE_SECTION_RE.sub("[TREE CONTENT NORMALIZED]", page_text)
    text = ASCII_TREE_BLOCK_RE.sub("[TREE CONTENT NORMALIZED]", text)
    text = FRONTMATTER_METADATA_RE.sub("", text)
    text = SECTION_ORDER_RE.sub("", text)
    text = re.sub(r"\[TREE CONTENT NORMALIZED\]\n+", "[TREE CONTENT NORMALIZED]\n", text)
    return text


class TestGedqMigrationContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run_command(sys.executable, "gen_site.py", str(GEDCOM_FILE), cwd=GEN_SITE_DIR)
        cls.model = GedcomModel()
        cls.model.parse_file(str(GEDCOM_FILE))
        cls.allowlist = json.loads(ALLOWLIST_FILE.read_text())
        cls.allowlist_paths = set(cls.allowlist["files"])

    def test_gedq_records_validate_against_published_schemas(self):
        person_schema = json.loads(run_command("gedq", "schema", "--mode", "person").stdout)
        family_schema = json.loads(run_command("gedq", "schema", "--mode", "family").stdout)
        source_schema = json.loads(run_command("gedq", "schema", "--mode", "source").stdout)
        event_schema = json.loads(run_command("gedq", "schema", "--mode", "event").stdout)
        note_schema = json.loads(run_command("gedq", "schema", "--mode", "note").stdout)

        validators = {
            "INDI": Draft202012Validator(person_schema),
            "FAM": Draft202012Validator(family_schema),
            "SOUR": Draft202012Validator(source_schema),
        }
        event_validator = Draft202012Validator(event_schema)
        note_validator = Draft202012Validator(note_schema)

        records_by_kind = {
            "INDI": load_jsonl_output("INDI"),
            "FAM": load_jsonl_output("FAM"),
            "SOUR": load_jsonl_output("SOUR"),
        }

        for kind, records in records_by_kind.items():
            for record in records:
                validators[kind].validate(
                    {
                        "kind": record["kind"],
                        "entity_id": record.get("entity_id"),
                        "src": record.get("src"),
                        "field_src": record.get("field_src"),
                    }
                )
                self.assertIsInstance(record.get("events", []), list)
                for event in record.get("events", []):
                    event_validator.validate(
                        {
                            "tag": event["tag"],
                            "src": event.get("src"),
                            "value": event.get("value"),
                            "type": event.get("type"),
                            "date": event.get("date"),
                            "place": event.get("place"),
                            "address": event.get("address"),
                            "source_ids": event.get("source_ids", []),
                            "associations": event.get("associations", []),
                            "notes": event.get("notes", []),
                            "note_src": event.get("note_src", []),
                            "note_refs": event.get("note_refs", []),
                            "age_at_event": event.get("age_at_event"),
                            "age_at_event_confidence": event.get("age_at_event_confidence", "unknown"),
                            "age_at_event_full": event.get("age_at_event_full"),
                            "age_at_event_min": event.get("age_at_event_min"),
                            "age_at_event_max": event.get("age_at_event_max"),
                            "age_at_event_period_start": event.get("age_at_event_period_start"),
                            "age_at_event_period_end": event.get("age_at_event_period_end"),
                            "age_at_event_source_text": event.get("age_at_event_source_text"),
                            "age_at_event_dual_year": event.get("age_at_event_dual_year"),
                            "age_at_event_era": event.get("age_at_event_era"),
                            "age_at_event_era_year": event.get("age_at_event_era_year"),
                            "age_at_event_min_era_year": event.get("age_at_event_min_era_year"),
                            "age_at_event_max_era_year": event.get("age_at_event_max_era_year"),
                            "age_at_event_calendar": event.get("age_at_event_calendar"),
                            "age_at_event_calendar_original": event.get("age_at_event_calendar_original"),
                            "age_at_event_parse_warning": event.get("age_at_event_parse_warning"),
                        }
                    )
                    for note_src in event.get("note_src", []):
                        note_validator.validate({"src": note_src["src"]})

                if kind == "INDI":
                    self.assertIsInstance(record.get("name_variants", []), list)
                    self.assertIn("sex", record)
                if kind == "FAM":
                    if "events" in record:
                        self.assertIsInstance(record["events"], list)
                if kind == "SOUR":
                    self.assertIn("source_text", record)

    def test_no_gedq_internal_imports(self):
        for path in [GEN_SITE_DIR / "adapter/gedq_adapter.py", GEN_SITE_DIR / "model/GedcomModel.py"]:
            text = path.read_text()
            self.assertNotIn("import gedq", text)
            self.assertNotIn("from gedq", text)

    def test_parser_layer_is_removed(self):
        self.assertFalse((GEN_SITE_DIR / "parser").exists())

        for path in (GEN_SITE_DIR / "model").glob("*.py"):
            text = path.read_text()
            self.assertNotIn("def parse(self, line", text)
            self.assertNotIn("GedcomParser", text)
            self.assertNotIn("GedcomLine", text)

    def test_generated_corpus_matches_baseline_except_allowlist(self):
        baseline_files = {
            line.strip()
            for line in run_command(
                "git",
                "ls-tree",
                "-r",
                "--name-only",
                BASELINE_COMMIT,
                "src/content/entity",
            ).stdout.splitlines()
            if line.strip()
        }
        current_files = {
            str(path.relative_to(WORKSPACE_DIR))
            for path in CONTENT_DIR.glob("*.md")
        }

        self.assertEqual(current_files, baseline_files)

        diff_paths = set()
        for rel_path in sorted(current_files):
            current_text = (WORKSPACE_DIR / rel_path).read_text()
            baseline_text = subprocess.run(
                ["git", "show", f"{BASELINE_COMMIT}:{rel_path}"],
                cwd=WORKSPACE_DIR,
                capture_output=True,
                text=True,
                check=True,
            ).stdout
            if normalize_tree_section(current_text) != normalize_tree_section(baseline_text):
                diff_paths.add(rel_path)

        self.assertEqual(diff_paths, self.allowlist_paths)

    def test_private_people_are_excluded(self):
        individual_files = sorted(CONTENT_DIR.glob("I*.md"))
        source_files = sorted(CONTENT_DIR.glob("S*.md"))

        self.assertEqual(len(individual_files), len(self.model.individuals))
        self.assertEqual(len(source_files), len(self.model.sources))
        self.assertEqual(len(individual_files) + len(source_files), 731)
        self.assertFalse((CONTENT_DIR / "I00001.md").exists())

    def test_known_witness_and_timestamp_match_baseline(self):
        path = CONTENT_DIR / "I00007.md"
        current = path.read_text()
        baseline = subprocess.run(
            ["git", "show", f"{BASELINE_COMMIT}:src/content/entity/I00007.md"],
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True,
            check=True,
        ).stdout

        self.assertEqual(normalize_tree_section(current), normalize_tree_section(baseline))
        self.assertIn('<pre class="ascii-tree-block">', current)
        self.assertNotIn('<details><summary>Toon</summary>', current)
        self.assertIn('- Geboorte tijdstip: "des morgens te tien ure"', current)
        self.assertIn('- Geboorte getuigen:', current)
        self.assertIn('Petrus Hoofman', current)

    def test_feature_categories_still_exist(self):
        individuals = self.model.individuals
        sources = self.model.sources

        self.assertTrue(any(len(individual.names) > 1 for individual in individuals))
        self.assertTrue(any(individual.sex for individual in individuals))
        self.assertTrue(any(individual.birth.date.value for individual in individuals))
        self.assertTrue(any(individual.death.date.value for individual in individuals))
        self.assertTrue(any(individual.baptism.date.value for individual in individuals))
        self.assertTrue(any(individual.burial.date.value for individual in individuals))
        self.assertTrue(any(individual.occupations for individual in individuals))
        self.assertTrue(any(individual.residences for individual in individuals))
        self.assertTrue(any(individual.facts for individual in individuals))
        self.assertTrue(any(individual.descriptions for individual in individuals))
        self.assertTrue(any(individual.associations for individual in individuals))
        self.assertTrue(any(individual.fams for individual in individuals))
        self.assertTrue(any(individual.sources for individual in individuals))
        self.assertTrue(any(event.sources for individual in individuals for event in individual.all_events()))
        self.assertTrue(any(source.repository and source.repository.www for source in sources))

    def test_generation_fails_cleanly_without_gedq(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = "."
        env["PATH"] = "/usr/bin:/bin"

        result = subprocess.run(
            [sys.executable, "gen_site.py", str(GEDCOM_FILE)],
            cwd=GEN_SITE_DIR,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        combined_output = f"{result.stdout}\n{result.stderr}"
        self.assertIn("gedq is required at version >= 2.0.0", combined_output)
