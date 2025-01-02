import argparse
import sys
from typing import Tuple, List, Dict
from GedcomParser import GedcomParser
from GedcomTransmission import GedcomTransmission
from Individual import Individual
from Family import Family
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags

def create_individual_diagram(transmission: GedcomTransmission, xref_id: str) -> str:
    """Create a PlantUML family diagram for an individual"""
    person = transmission.individuals[xref_id]
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
    if person.famc:
        family = transmission.families[person.famc]
        parent_details = [transmission.individuals[family.husband], transmission.individuals[family.wife]]
        for i, parent in enumerate(parent_details):
            diagram.append(f'class "{parent.name}" as P{i} #lightgreen {{')
            birth_date = parent.birth_date if parent.birth_date else "?"
            birth_place = parent.birth_place if parent.birth_place else "?"
            death_date = parent.death_date if parent.death_date else "?"
            death_place = parent.death_place if parent.death_place else "?"
            diagram.append(f'<&plus> {birth_date} {birth_place}')
            diagram.append(f'<&x> {death_date} {death_place}')
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
    birth_date = person.birth_date if person.birth_date else "?"
    birth_place = person.birth_place if person.birth_place else "?"
    death_date = person.death_date if person.death_date else "?"
    death_place = person.death_place if person.death_place else "?"
    diagram.append(f'<&plus> {birth_date} {birth_place}')
    diagram.append(f'<&x> {death_date} {death_place}')
    diagram.append("}")

    # Add spouse and children
    for fam_id in person.fams:
        family = transmission.families[fam_id]
        spouse_id = family.husband if family.husband != xref_id else family.wife
        spouse = transmission.individuals[spouse_id]

        diagram.append("")
        diagram.append(f'class "{spouse.name}" as S1 #lightcoral {{')
        birth_date = spouse.birth_date if spouse.birth_date else "?"
        birth_place = spouse.birth_place if spouse.birth_place else "?"
        death_date = spouse.death_date if spouse.death_date else "?"
        death_place = spouse.death_place if spouse.death_place else "?"
        diagram.append(f'<&plus> {birth_date} {birth_place}')
        diagram.append(f'<&x> {death_date} {death_place}')
        diagram.append("}")

        if family.marriage_date:
            diagram.append(f'class "Marriage" as M2 #lightyellow {{')
            diagram.append(f'<&people> {family.marriage_date if family.marriage_date else "?"}')
            diagram.append("}")

        for i, child_id in enumerate(family.children):
            child = transmission.individuals[child_id]
            diagram.append(f'class "{child.name}" as C{i} #pink {{')
            birth_date = child.birth_date if child.birth_date else "?"
            birth_place = child.birth_place if child.birth_place else "?"
            death_date = child.death_date if child.death_date else "?"
            death_place = child.death_place if child.death_place else "?"
            diagram.append(f'<&plus> {birth_date} {birth_place}')
            diagram.append(f'<&x> {death_date} {death_place}')
            diagram.append("}")

        # Add relationships
        diagram.append(f'{xref_id.strip("@")} -- M2')
        diagram.append(f'S1 -- M2')
        for i in range(len(family.children)):
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
