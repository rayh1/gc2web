from subprocess import CompletedProcess
from unittest import TestCase
from unittest.mock import patch

from adapter.gedq_adapter import REQUIRED_GEDQ_VERSION
from adapter.gedq_adapter import build_families
from adapter.gedq_adapter import build_individuals
from adapter.gedq_adapter import ensure_gedq_compatible
from adapter.gedq_adapter import format_version
from adapter.gedq_adapter import load_dataset
from adapter.gedq_adapter import parse_version


class TestGedqAdapter(TestCase):
    def test_parse_version(self):
        self.assertEqual(parse_version("2.0.0\n"), (2, 0, 0))

    def test_parse_version_rejects_invalid_value(self):
        with self.assertRaises(ValueError):
            parse_version("version-two")

    @patch("adapter.gedq_adapter.subprocess.run")
    def test_ensure_gedq_compatible_rejects_missing_binary(self, run_mock):
        run_mock.side_effect = FileNotFoundError()

        with self.assertRaisesRegex(
            RuntimeError,
            rf"gedq is required at version >= {format_version(REQUIRED_GEDQ_VERSION)}",
        ):
            ensure_gedq_compatible()

    @patch("adapter.gedq_adapter.subprocess.run")
    def test_ensure_gedq_compatible_rejects_old_version(self, run_mock):
        run_mock.return_value = CompletedProcess(["gedq", "--version"], 0, stdout="1.9.9\n", stderr="")

        with self.assertRaisesRegex(RuntimeError, r"found 1\.9\.9"):
            ensure_gedq_compatible()

    @patch("adapter.gedq_adapter.subprocess.run")
    def test_load_dataset_reads_each_kind(self, run_mock):
        run_mock.side_effect = [
            CompletedProcess(["gedq", "--version"], 0, stdout="2.0.0\n", stderr=""),
            CompletedProcess(["gedq", "search"], 0, stdout='{"entity_id":"I1"}\n', stderr=""),
            CompletedProcess(["gedq", "search"], 0, stdout='{"entity_id":"F1"}\n', stderr=""),
            CompletedProcess(["gedq", "search"], 0, stdout='{"entity_id":"S1"}\n', stderr=""),
            CompletedProcess(["gedq", "search"], 0, stdout='{"entity_id":"R1"}\n', stderr=""),
        ]

        dataset = load_dataset("gen_site/Hoofman.ged")

        self.assertEqual(dataset.individuals, [{"entity_id": "I1"}])
        self.assertEqual(dataset.families, [{"entity_id": "F1"}])
        self.assertEqual(dataset.sources, [{"entity_id": "S1"}])
        self.assertEqual(dataset.repositories, [{"entity_id": "R1"}])

    def test_build_families_normalizes_scalar_child_id(self):
        families = build_families(
            [
                {
                    "entity_id": "F1",
                    "husb": "I1",
                    "wife": "I2",
                    "chil": "I3",
                }
            ]
        )

        self.assertEqual(families["F1"].children_ids, ["I3"])

    def test_build_families_preserves_child_id_list(self):
        families = build_families(
            [
                {
                    "entity_id": "F1",
                    "chil": ["I3", "I4"],
                }
            ]
        )

        self.assertEqual(families["F1"].children_ids, ["I3", "I4"])

    def test_build_individuals_normalizes_scalar_source_id(self):
        individuals = build_individuals(
            [
                {
                    "entity_id": "I1",
                    "name": "Test /Person/",
                    "name_variants": ["Test /Person/"],
                    "source_ids": "S1",
                }
            ],
            [],
        )

        self.assertEqual(individuals["I1"].source_ids, ["S1"])

    def test_build_individuals_preserves_source_id_list(self):
        individuals = build_individuals(
            [
                {
                    "entity_id": "I1",
                    "name": "Test /Person/",
                    "name_variants": ["Test /Person/"],
                    "source_ids": ["S1", "S2"],
                }
            ],
            [],
        )

        self.assertEqual(individuals["I1"].source_ids, ["S1", "S2"])

    def test_build_individuals_prefers_name_occurrences_for_sources_and_notes(self):
        individuals = build_individuals(
            [
                {
                    "entity_id": "I1",
                    "name": "Primary /Person/",
                    "name_variants": ["Primary /Person/"],
                    "names": [
                        {
                            "name_index": 0,
                            "value": "Primary /Person/",
                            "source_ids": ["S2", "S1"],
                            "notes": ["Alias explanation"],
                            "src": {"file": "gen_site/Hoofman.ged", "line": 42},
                        },
                        {
                            "name_index": 1,
                            "value": "Alt /Person/",
                            "source_ids": ["S3"],
                            "notes": [],
                            "src": {"file": "gen_site/Hoofman.ged", "line": 43},
                        },
                    ],
                }
            ],
            [
                {
                    "entity_id": "S9",
                    "CITES": [
                        {
                            "subject_kind": "name",
                            "entity_id": "I1",
                            "value": "Primary /Person/",
                        }
                    ],
                }
            ],
        )

        primary_name, alternate_name = individuals["I1"].names

        self.assertEqual(primary_name.source_ids, ["S2", "S1"])
        self.assertEqual([note.value for note in primary_name.notes], ["Alias explanation"])
        self.assertEqual([note.line_num for note in primary_name.notes], [42])
        self.assertEqual(alternate_name.source_ids, ["S3"])

    def test_build_individuals_falls_back_to_name_variant_cites_when_names_missing(self):
        individuals = build_individuals(
            [
                {
                    "entity_id": "I1",
                    "name": "Primary /Person/",
                    "name_variants": ["Primary /Person/", "Alt /Person/"],
                }
            ],
            [
                {
                    "entity_id": "S1",
                    "CITES": [
                        {
                            "subject_kind": "name",
                            "entity_id": "I1",
                            "value": "Primary /Person/",
                        }
                    ],
                },
                {
                    "entity_id": "S2",
                    "CITES": [
                        {
                            "subject_kind": "name",
                            "entity_id": "I1",
                            "value": "Alt /Person/",
                        }
                    ],
                },
            ],
        )

        primary_name, alternate_name = individuals["I1"].names

        self.assertEqual(primary_name.source_ids, ["S1"])
        self.assertEqual(alternate_name.source_ids, ["S2"])
