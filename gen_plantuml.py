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

def create_individual_diagram(transmission: GedcomTransmission, xref_id: str) -> str:
    """Create a PlantUML family diagram for an individual"""
    person = transmission.get_individual(xref_id)
    diagram = [
        "@startuml",
        "skinparam backgroundColor transparent",
        "skinparam roundcorner 20",
        "hide circle",
        "hide empty members",
        "",
        "' Parents",
    ]

    # Add parents
    family = person.famc
    if family:
        parent_details = [family.husband, family.wife]
        for i, parent in enumerate(parent_details):
            diagram.append(f'class "{parent.name}" as P{i} #lightgreen {{')
            diagram.append(f'<&plus> {s(parent.birth_date)} {s(parent.birth_place)}')
            diagram.append(f'<&x> {s(parent.death_date)} {s(parent.death_place)}')
            diagram.append("}")

        if family.marriage_date:
            diagram.append(f'class "Marriage" as M1 #lightyellow {{')
            diagram.append(f'<&people> {family.marriage_date if family.marriage_date else "?"}')
            diagram.append("}")

        # Add relationships from parents to marriage block
        diagram.append(f'P0 -- M1')
        diagram.append(f'P1 -- M1')
        diagram.append(f'M1 -- {xref_id.strip("@")}')

    # Add main individual
    diagram.append("")
    diagram.append(f'class "{person.name}" as {xref_id.strip("@")} #lightblue {{')
    diagram.append(f'<&plus> {s(person.birth_date)} {s(person.birth_place)}')
    diagram.append(f'<&x> {s(person.death_date)} {s(person.death_place)}')
    diagram.append("}")

    # Add spouse and children
    for family in person.fams:
        spouse_id = family.husband_id if family.husband_id != xref_id else family.wife_id
        spouse = transmission.get_individual(spouse_id)

        diagram.append("")
        diagram.append(f'class "{spouse.name}" as S1 #lightcoral {{')
        diagram.append(f'<&plus> {s(spouse.birth_date)} {s(spouse.birth_place)}')
        diagram.append(f'<&x> {s(spouse.death_date)} {s(spouse.death_place)}')
        diagram.append("}")

        if family.marriage_date:
            diagram.append(f'class "Marriage" as M2 #lightyellow {{')
            diagram.append(f'<&people> {family.marriage_date if family.marriage_date else "?"}')
            diagram.append("}")

        for i, child in enumerate(family.children):
            diagram.append(f'class "{child.name}" as C{i} #pink {{')
            diagram.append(f'<&plus> {s(child.birth_date)} {s(child.birth_place)}')
            diagram.append(f'<&x> {s(child.death_date)} {s(child.death_place)}')
            diagram.append("}")

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
