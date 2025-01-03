import argparse
import sys
from typing import Tuple, List, Dict
from GedcomParser import GedcomParser
from GedcomTransmission import GedcomTransmission
from Individual import Individual
from Family import Family
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags

def s(value: str) -> str:
    return value if value else "?"

def add_individual_to_diagram(diagram: List[str], individual: Individual, box_name: str, color: str = None, stereotype: str = None):
    if color is None:
        if individual.is_male:
            color = '#lightblue'
        elif individual.is_female:
            color = '#pink'
        else:
            color = '#lightgrey'
    stereotype = f'<<{stereotype}>>' if stereotype else ''
    diagram.append(f'class "{individual.name}" as {box_name} {stereotype} {color} {{')
    diagram.append(f'{{field}} <&plus> {s(individual.birth_date)} {s(individual.birth_place)}')
    diagram.append(f'{{field}} <&x> {s(individual.death_date)} {s(individual.death_place)}')
    diagram.append("}")

def add_marriage_to_diagram(diagram: List[str], family: Family, box_name: str, color: str = None):
    if color is None:
        color = '#lightyellow'
    diagram.append(f'class "<&people> {family.marriage_date if family.marriage_date else "?"}" as {box_name} {color} {{')
    diagram.append("}")

def create_individual_diagram(transmission: GedcomTransmission, xref_id: str) -> str:
    """Create a PlantUML family diagram for an individual"""
    person = transmission.get_individual(xref_id)
    diagram = [
        "@startuml",
        "skinparam backgroundColor transparent",
        "skinparam roundcorner 20",
        "hide circle",
        "hide empty members",
        "hide stereotype",
        "",
        "skinparam class {",
        "   BorderThickness<<main>> 2",
        "}",
        "",
        "' Parents",
    ]

    # Add parents
    family = person.famc
    if family:
        parents = [family.husband, family.wife]
        for i, parent in enumerate(parents):
            add_individual_to_diagram(diagram, parent, f'P{i}')

        if family.marriage_date:
            add_marriage_to_diagram(diagram, family, "M1")

        # Add relationships from parents to marriage block
        diagram.append(f'P0 -- M1')
        diagram.append(f'P1 -- M1')
        diagram.append(f'M1 -- {xref_id.strip("@")}')

    # Add main individual
    diagram.append("")
    add_individual_to_diagram(diagram, person, xref_id.strip("@"), '#lightgreen', stereotype="main")

    # Add spouse and children
    for family in person.fams:
        spouse_id = family.husband_id if family.husband_id != xref_id else family.wife_id
        spouse = transmission.get_individual(spouse_id)

        diagram.append("")
        add_individual_to_diagram(diagram, spouse, 'S1')

        add_marriage_to_diagram(diagram, family, "M2")

        for i, child in enumerate(family.children):
            add_individual_to_diagram(diagram, child, f'C{i}')

        # Add relationships
        diagram.append(f'{xref_id.strip("@")} -- M2')
        diagram.append(f'S1 -- M2')
        for i in range(len(family.children_ids)):
            diagram.append(f'M2 -- C{i}')

    diagram.extend(["", "@enduml"])
    return "\n".join(diagram)

def main(argv: List[str]):
    ap = argparse.ArgumentParser(description='Process a GEDCOM file.')
    ap.add_argument('file', type=str, help='Path to the GEDCOM file')
    ap.add_argument('-i', '--id', type=str, required=False, nargs='?', default=None, help='Id of Gedcom line')
    
    args = ap.parse_args(argv[1:])

    with open(args.file, 'r') as gedcom_stream:
        parser = GedcomParser()
        transmission = parser.parse(gedcom_stream)
        transmission.parse_gedcom()

        print(create_individual_diagram(transmission, args.id))

# Example usage
if __name__ == '__main__':
    main(sys.argv)
