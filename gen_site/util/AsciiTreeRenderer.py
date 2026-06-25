from dataclasses import dataclass
from datetime import datetime
from html import escape

from model.Family import Family
from model.Individual import Individual


@dataclass(frozen=True)
class AsciiTreeLine:
    text: str
    is_focus: bool = False
    html: str | None = None


@dataclass(frozen=True)
class _FamilyBranch:
    label: AsciiTreeLine
    children: list[AsciiTreeLine]


def render_ascii_tree(individual: Individual, max_spouse_families: int = 2) -> list[AsciiTreeLine]:
    parent_chain = [parent for parent in [individual.father, individual.mother] if parent]
    focus_line = AsciiTreeLine(_person_label(individual, is_focus=True), is_focus=True)

    lines: list[AsciiTreeLine] = []
    descendant_prefix = ""

    if parent_chain:
        lines.append(_linked_line("", _person_label(parent_chain[0]), parent_chain[0]))
        if len(parent_chain) > 1:
            lines.append(_linked_line("└── x ", _person_label(parent_chain[1]), parent_chain[1]))
            descendant_prefix = "    "
        else:
            descendant_prefix = "    "

        sibling_group = sorted([*individual.siblings(), individual], key=lambda person: person.start_life.date.date() or datetime.max)
        for index, sibling in enumerate(sibling_group):
            connector = "└──" if index == len(sibling_group) - 1 else "├──"
            is_focus = sibling.xref_id == individual.xref_id
            label = _person_label(sibling, is_focus=is_focus)
            lines.append(_linked_line(f"{descendant_prefix}{connector} ", label, sibling, is_focus=is_focus))
            if is_focus:
                _append_family_branches(lines, individual, f"{descendant_prefix}{'    ' if connector == '└──' else '│   '}", max_spouse_families)
    else:
        lines.append(_linked_line("", focus_line.text, individual, is_focus=True))
        _append_family_branches(lines, individual, "", max_spouse_families)

    return lines


def _append_family_branches(
    lines: list[AsciiTreeLine],
    individual: Individual,
    prefix: str,
    max_spouse_families: int,
) -> None:
    branches = _family_branches(individual, max_spouse_families)
    if not branches:
        return

    for index, branch in enumerate(branches):
        is_last_branch = index == len(branches) - 1
        connector = "└──" if is_last_branch else "├──"
        label_html = branch.label.html if branch.label.html is not None else escape(branch.label.text)
        lines.append(AsciiTreeLine(f"{prefix}{connector} {branch.label.text}", html=f"{escape(prefix + connector + ' ')}{label_html}"))

        child_prefix = prefix + ("    " if is_last_branch else "│   ")
        for child_index, child_label in enumerate(branch.children):
            child_connector = "└──" if child_index == len(branch.children) - 1 else "├──"
            child_html = child_label.html if child_label.html is not None else escape(child_label.text)
            lines.append(AsciiTreeLine(f"{child_prefix}{child_connector} {child_label.text}", html=f"{escape(child_prefix + child_connector + ' ')}{child_html}"))


def render_ascii_tree_block(individual: Individual, max_spouse_families: int = 2) -> str:
    rendered_lines: list[str] = []
    for line in render_ascii_tree(individual, max_spouse_families=max_spouse_families):
        rendered_body = line.html if line.html is not None else escape(line.text)
        if line.is_focus:
            rendered_lines.append(f'<span class="ascii-tree__focus">{rendered_body}</span>')
        else:
            rendered_lines.append(rendered_body)

    return "\n".join(
        [
            '<div class="ascii-tree-wrap">',
            '<pre class="ascii-tree-block">',
            *rendered_lines,
            '</pre>',
            '</div>',
        ]
    )


def _family_branches(individual: Individual, max_spouse_families: int) -> list[_FamilyBranch]:
    families = list(individual.fams)
    visible_families = families[:max_spouse_families]
    hidden_count = max(len(families) - len(visible_families), 0)

    branches: list[_FamilyBranch] = []
    for family in visible_families:
        branch = _family_branch(individual, family)
        if branch:
            branches.append(branch)

    if hidden_count:
        noun = "family branch" if hidden_count == 1 else "family branches"
        branches.append(_FamilyBranch(AsciiTreeLine(f"… {hidden_count} more {noun} not shown"), []))

    return branches


def _family_branch(individual: Individual, family: Family) -> _FamilyBranch | None:
    spouse = family.spouse(individual)
    children = sorted(family.children, key=lambda child: child.start_life.date.date() or datetime.max)
    child_labels = [_linked_line("", _person_label(child), child) for child in children]

    if spouse:
        return _FamilyBranch(_linked_line("x ", _person_label(spouse), spouse), child_labels)
    if child_labels:
        return _FamilyBranch(AsciiTreeLine("Kinderen"), child_labels)
    return None


def _person_label(individual: Individual, is_focus: bool = False) -> str:
    label = f"{individual.name} {_lifespan_years(individual)}"
    return label


def _linked_line(prefix: str, label: str, individual: Individual, is_focus: bool = False) -> AsciiTreeLine:
    href = f"../{individual.xref_id.lower()}/"
    html = f"{escape(prefix)}<a class=\"ascii-tree-link\" href=\"{href}\">{escape(label)}</a>"
    return AsciiTreeLine(f"{prefix}{label}", is_focus=is_focus, html=html)


def _lifespan_years(individual: Individual) -> str:
    start_date = individual.start_life.date.date()
    end_date = individual.end_life.date.date()
    start_year = start_date.year if start_date and start_date.year else "?"
    end_year = end_date.year if end_date and end_date.year else "?"
    return f"({start_year}-{end_year})"
