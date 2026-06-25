from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from gen_site import generate_individual_page
from model.GedcomModel import GedcomModel


class TestAsciiTreeGeneration(TestCase):
    @classmethod
    def setUpClass(cls):
        GedcomModel().parse_file("/workspace/gen_site/Hoofman.ged")

    def test_generate_individual_page_emits_visible_ascii_tree_block(self):
        individual = GedcomModel().get_individual("I00007")
        self.assertIsNotNone(individual)

        with TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "I00007.md"
            generate_individual_page(individual, output_path)  # type: ignore[arg-type]
            content = output_path.read_text()

        self.assertIn('<pre class="ascii-tree-block">', content)
        self.assertIn("ascii-tree__focus", content)
        self.assertIn('class="ascii-tree-link"', content)
        self.assertIn('href="../i00013/"', content)
        self.assertIn("├──", content)
        self.assertIn("x ", content)
        self.assertNotIn("<details><summary>Toon</summary>", content)
        self.assertNotIn("plantuml/svg", content)
