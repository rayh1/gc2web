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

def add_individual_to_diagram(diagram: List[str], individual: Individual, color: str = None, stereotype: str = None):
    if color is None:
        if individual.is_male:
            color = '#E3F5FB'
        elif individual.is_female:
            color = '#FBE3E3'
        else:
            color = '#lightgrey'
    stereotype = f'<<{stereotype}>>' if stereotype else ''
    diagram.append(f'class "{individual.name}" as {individual.xref_id} {stereotype} {color} {{')
    
    birth_date = s(individual.birth_date) if individual.birth_date else s(individual.baptism_date)
    birth_place = s(individual.birth_place) if individual.birth_place else s(individual.baptism_place)
    diagram.append(f'{{field}} <:baby_bottle:> {birth_date} {birth_place}')
    
    death_date = s(individual.death_date) if individual.death_date else s(individual.burial_date)
    death_place = s(individual.death_place) if individual.death_place else s(individual.burial_place)
    diagram.append(f'{{field}} <:skull_and_crossbones:> {death_date} {death_place}')
    
    diagram.append("}")

def add_marriage_to_diagram(diagram: List[str], family: Family, color: str = None):
    if color is None:
        color = '#lightyellow'
    diagram.append(f'class "<:wedding:> {s(family.marriage_date)}" as {family.xref_id} {color} {{')
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
        add_individual_to_diagram(diagram, family.husband)
        add_individual_to_diagram(diagram, family.wife)

        add_marriage_to_diagram(diagram, family)

        diagram.append(f'{family.husband.xref_id} -- {family.xref_id}')
        diagram.append(f'{family.wife.xref_id} -- {family.xref_id}')
        diagram.append(f'{family.xref_id} -- {xref_id}')

    # Add main individual
    diagram.append("")
    add_individual_to_diagram(diagram, person, stereotype="main")

    # Add spouse and children
    for family in person.fams:
        spouse_id = family.husband_id if family.husband_id != xref_id else family.wife_id
        spouse = transmission.get_individual(spouse_id)

        diagram.append("")
        add_individual_to_diagram(diagram, spouse)

        add_marriage_to_diagram(diagram, family)

        for i, child in enumerate(family.children):
            add_individual_to_diagram(diagram, child)

        # Add relationships
        diagram.append(f'{xref_id} -- {family.xref_id}')
        diagram.append(f'{spouse.xref_id} -- {family.xref_id}')
        for child in family.children:
            diagram.append(f'{family.xref_id} -- {child.xref_id}')

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
