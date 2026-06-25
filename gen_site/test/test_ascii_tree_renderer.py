from unittest import TestCase

from model.Family import Family
from model.Individual import Individual
from model.Name import Name
from util.AsciiTreeRenderer import render_ascii_tree


class TestAsciiTreeRenderer(TestCase):
    def test_render_ascii_tree_includes_direct_family_scope(self):
        father = self._person("I1", "Petrus Hoofman", "1833", "1874", sex="M")
        mother = self._person("I2", "Constantia Engels", "1838", "1915", sex="F")
        focus = self._person("I3", "Augustinus Hoofman", "1860", "1918", sex="M")
        spouse = self._person("I4", "Maria Antoinetta Rozema", "1862", None, sex="F")
        child = self._person("I5", "Petrus Johannes Hoofman", "1888", "1890", sex="M")

        self._set_parent_family(focus, father=father, mother=mother)
        self._add_spouse_family(focus, spouse=spouse, children=[child])

        lines = render_ascii_tree(focus)
        rendered = [line.text for line in lines]

        self.assertEqual(sum(1 for line in lines if line.is_focus), 1)
        self.assertIn("Petrus Hoofman (1833-1874)", rendered[0])
        self.assertEqual(rendered[1], "└── x Constantia Engels (1838-1915)")
        self.assertEqual(rendered[2], "    └── Augustinus Hoofman (1860-1918)")
        self.assertTrue(any("x Maria Antoinetta Rozema (1862-?)" in line for line in rendered))
        self.assertTrue(any("Petrus Johannes Hoofman (1888-1890)" in line for line in rendered))

    def test_render_ascii_tree_falls_back_to_single_focus_line(self):
        focus = self._person("I1", "Solo Person", None, None, sex="U")

        lines = render_ascii_tree(focus)

        self.assertEqual([line.text for line in lines], ["Solo Person (?-?)"])
        self.assertTrue(lines[0].is_focus)

    def test_render_ascii_tree_handles_one_known_parent(self):
        parent = self._person("I1", "Known Parent", "1800", "1860", sex="F")
        focus = self._person("I2", "Child Person", "1835", None, sex="F")

        self._set_parent_family(focus, mother=parent)

        lines = render_ascii_tree(focus)
        rendered = [line.text for line in lines]

        self.assertEqual(rendered[0], "Known Parent (1800-1860)")
        self.assertEqual(rendered[1], "    └── Child Person (1835-?)")

    def test_render_ascii_tree_includes_siblings_in_birth_order(self):
        father = self._person("I1", "Father Person", "1800", "1870", sex="M")
        mother = self._person("I2", "Mother Person", "1802", "1880", sex="F")
        older_sibling = self._person("I3", "Older Sibling", "1830", None, sex="F")
        focus = self._person("I4", "Focus Person", "1835", None, sex="M")
        younger_sibling = self._person("I5", "Younger Sibling", "1840", None, sex="F")

        family = Family()
        family.xref_id = "F-siblings"
        family.husband_id = father.xref_id
        family.wife_id = mother.xref_id
        family.children_ids = [older_sibling.xref_id, focus.xref_id, younger_sibling.xref_id]
        family._Family__husband_cache = father
        family._Family__wife_cache = mother
        family._Family__children_cache = [older_sibling, focus, younger_sibling]

        for child in [older_sibling, focus, younger_sibling]:
            child._Individual__famc_id = family.xref_id
            child._Individual__famc_cache = family

        rendered = [line.text for line in render_ascii_tree(focus)]

        self.assertEqual(rendered[0], "Father Person (1800-1870)")
        self.assertEqual(rendered[1], "└── x Mother Person (1802-1880)")
        self.assertEqual(rendered[2], "    ├── Older Sibling (1830-?)")
        self.assertEqual(rendered[3], "    ├── Focus Person (1835-?)")
        self.assertEqual(rendered[4], "    └── Younger Sibling (1840-?)")

    def test_render_ascii_tree_reduces_extra_spouse_families_deterministically(self):
        focus = self._person("I1", "Multi Family", "1830", "1900", sex="M")
        spouse_one = self._person("I2", "Spouse One", "1831", None, sex="F")
        spouse_two = self._person("I3", "Spouse Two", "1832", None, sex="F")
        spouse_three = self._person("I4", "Spouse Three", "1833", None, sex="F")

        self._add_spouse_family(focus, spouse=spouse_one, children=[])
        self._add_spouse_family(focus, spouse=spouse_two, children=[])
        self._add_spouse_family(focus, spouse=spouse_three, children=[])

        rendered = [line.text for line in render_ascii_tree(focus, max_spouse_families=2)]

        self.assertTrue(any("x Spouse One (1831-?)" in line for line in rendered))
        self.assertTrue(any("x Spouse Two (1832-?)" in line for line in rendered))
        self.assertFalse(any("x Spouse Three (1833-?)" in line for line in rendered))
        self.assertTrue(any("… 1 more family branch not shown" in line for line in rendered))

    def _person(
        self,
        xref_id: str,
        plain_name: str,
        birth_year: str | None,
        death_year: str | None,
        sex: str,
    ) -> Individual:
        individual = Individual()
        individual.xref_id = xref_id
        individual.sex = sex

        name = Name()
        name.value = plain_name
        individual.add_name(name)

        individual.birth.date.value = birth_year
        individual.death.date.value = death_year
        return individual

    def _set_parent_family(
        self,
        child: Individual,
        father: Individual | None = None,
        mother: Individual | None = None,
    ) -> None:
        family = Family()
        family.xref_id = f"F-{child.xref_id}-parents"
        family.husband_id = father.xref_id if father else None
        family.wife_id = mother.xref_id if mother else None
        family.children_ids = [child.xref_id]
        family._Family__husband_cache = father
        family._Family__wife_cache = mother
        family._Family__children_cache = [child]

        child._Individual__famc_id = family.xref_id
        child._Individual__famc_cache = family

    def _add_spouse_family(
        self,
        individual: Individual,
        spouse: Individual | None,
        children: list[Individual],
    ) -> None:
        family = Family()
        family.xref_id = f"F-{individual.xref_id}-{len(individual.fams)}"

        if individual.sex == "F":
            family.wife_id = individual.xref_id
            family.husband_id = spouse.xref_id if spouse else None
            family._Family__wife_cache = individual
            family._Family__husband_cache = spouse
        else:
            family.husband_id = individual.xref_id
            family.wife_id = spouse.xref_id if spouse else None
            family._Family__husband_cache = individual
            family._Family__wife_cache = spouse

        family.children_ids = [child.xref_id for child in children]
        family._Family__children_cache = children

        current_fams = list(individual.fams)
        current_fams.append(family)
        individual._Individual__fams_ids = [fam.xref_id for fam in current_fams]
        individual._Individual__fams_cache = current_fams
