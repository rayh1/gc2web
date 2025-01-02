import argparse
import sys
from typing import Tuple, List, Dict
from GedcomParser import GedcomParser
from GedcomTransmission import GedcomTransmission
from GedcomLine import GedcomLine
from GedcomTags import GedcomTags

def extract_date_place(transmission: GedcomTransmission, line: GedcomLine) -> tuple[str, str]:
    """Extract date and place from a GEDCOM event line"""
    date = ""
    place = ""
    for subline in transmission.iterate(line):
        if subline.tag == GedcomTags.DATE:
            date = subline.value if subline.value else ""
        elif subline.tag == GedcomTags.PLAC:
            place = subline.value if subline.value else ""
    return date, place

def find_person_details(transmission: GedcomTransmission, xref_id: str) -> dict:
    """Find name, birth, death details for a person"""
    details = {
        'name': 'Unknown',
        'birth_date': '',
        'birth_place': '',
        'death_date': '',
        'death_place': ''
    }
    
    # Find name
    for line in transmission.iterate_id(xref_id, tag=GedcomTags.NAME):
        details['name'] = line.value if line.value else "Unknown"
        break
        
    # Find birth info
    for line in transmission.iterate_id(xref_id, tag=GedcomTags.BIRT):
        details['birth_date'], details['birth_place'] = extract_date_place(transmission, line)
            
    # Find death info
    for line in transmission.iterate_id(xref_id, tag=GedcomTags.DEAT):
        details['death_date'], details['death_place'] = extract_date_place(transmission, line)
    
    return details

def find_family_members(transmission: GedcomTransmission, xref_id: str) -> tuple[list, list, str]:
    """Find parents, children and marriage date for a person"""
    parents = []
    children = []
    marriage_date = ""
    
    # Find family where person is child
    for famc in transmission.iterate_id(xref_id, tag=GedcomTags.FAMC):
        if famc.pointer_value:
            # Get parents from this family
            for family in transmission.iterate_id(famc.pointer_value):
                if family.tag == GedcomTags.HUSB and family.pointer_value:
                    parents.append(family.pointer_value)
                elif family.tag == GedcomTags.WIFE and family.pointer_value:
                    parents.append(family.pointer_value)
                elif family.tag == GedcomTags.MARR:
                    date, _ = extract_date_place(transmission, family)
                    marriage_date = date
    
    # Find families where person is parent
    for fams in transmission.iterate_id(xref_id, tag=GedcomTags.FAMS):
        if fams.pointer_value:
            # Get children from this family
            for family in transmission.iterate_id(fams.pointer_value):
                if family.tag == GedcomTags.CHIL and family.pointer_value:
                    children.append(family.pointer_value)
    
    return parents, children, marriage_date

def find_spouse_details(transmission: GedcomTransmission, xref_id: str) -> dict:
    """Find name, birth, death details for a spouse"""
    details = {
        'name': 'Unknown',
        'birth_date': '',
        'birth_place': '',
        'death_date': '',
        'death_place': ''
    }
    
    # Find name
    for line in transmission.iterate_id(xref_id, tag=GedcomTags.NAME):
        details['name'] = line.value if line.value else "Unknown"
        break
        
    # Find birth info
    for line in transmission.iterate_id(xref_id, tag=GedcomTags.BIRT):
        details['birth_date'], details['birth_place'] = extract_date_place(transmission, line)
            
    # Find death info
    for line in transmission.iterate_id(xref_id, tag=GedcomTags.DEAT):
        details['death_date'], details['death_place'] = extract_date_place(transmission, line)
    
    return details

def find_spouse(transmission: GedcomTransmission, xref_id: str) -> tuple[dict, str]:
    """Find spouse details and marriage date for a person"""
    spouse = {}
    marriage_date = ""
    
    # Find families where person is parent
    for fams in transmission.iterate_id(xref_id, tag=GedcomTags.FAMS):
        if fams.pointer_value:
            for family in transmission.iterate_id(fams.pointer_value):
                if family.tag == GedcomTags.HUSB and family.pointer_value != xref_id:
                    spouse = find_spouse_details(transmission, family.pointer_value)
                elif family.tag == GedcomTags.WIFE and family.pointer_value != xref_id:
                    spouse = find_spouse_details(transmission, family.pointer_value)
                elif family.tag == GedcomTags.MARR:
                    date, _ = extract_date_place(transmission, family)
                    marriage_date = date
    
    return spouse, marriage_date

def create_individual_diagram(transmission: GedcomTransmission, xref_id: str) -> str:
    """Create a PlantUML family diagram for an individual"""
    
    # Get details for main individual
    person = find_person_details(transmission, xref_id)
    
    # Find family members
    parents, children, parents_marriage = find_family_members(transmission, xref_id)
    
    # Get details for parents
    parent_details = [find_person_details(transmission, p) for p in parents]
    
    # Get details for children
    child_details = [find_person_details(transmission, c) for c in children]
    
    # Get details for spouse
    spouse, marriage_date = find_spouse(transmission, xref_id)
    
    # Create PlantUML diagram
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
    for i, parent in enumerate(parent_details):
        diagram.append(f'class "{parent["name"]}" as P{i} #lightgreen {{')
        birth_date = parent['birth_date'] if parent['birth_date'] else "?"
        birth_place = parent['birth_place'] if parent['birth_place'] else "?"
        death_date = parent['death_date'] if parent['death_date'] else "?"
        death_place = parent['death_place'] if parent['death_place'] else "?"
        diagram.append(f'<&plus> {birth_date} {birth_place}')
        diagram.append(f'<&x> {death_date} {death_place}')
        diagram.append("}")
        
    if parents_marriage:
        diagram.append(f'class "Marriage" as M1 #lightyellow {{')
        diagram.append(f'<&people> {parents_marriage if parents_marriage else "?"}')
        diagram.append("}")
    
    # Add main individual
    diagram.append("")
    diagram.append(f'class "{person["name"]}" as {xref_id.strip("@")} #lightblue {{')
    birth_date = person['birth_date'] if person['birth_date'] else "?"
    birth_place = person['birth_place'] if person['birth_place'] else "?"
    death_date = person['death_date'] if person['death_date'] else "?"
    death_place = person['death_place'] if person['death_place'] else "?"
    diagram.append(f'<&plus> {birth_date} {birth_place}')
    diagram.append(f'<&x> {death_date} {death_place}')
    diagram.append("}")
    
    # Add spouse
    if spouse:
        diagram.append("")
        diagram.append(f'class "{spouse["name"]}" as S1 #lightcoral {{')
        birth_date = spouse['birth_date'] if spouse['birth_date'] else "?"
        birth_place = spouse['birth_place'] if spouse['birth_place'] else "?"
        death_date = spouse['death_date'] if spouse['death_date'] else "?"
        death_place = spouse['death_place'] if spouse['death_place'] else "?"
        diagram.append(f'<&plus> {birth_date} {birth_place}')
        diagram.append(f'<&x> {death_date} {death_place}')
        diagram.append("}")
        
        if marriage_date:
            diagram.append(f'class "Marriage" as M2 #lightyellow {{')
            diagram.append(f'<&people> {marriage_date if marriage_date else "?"}')
            diagram.append("}")
    
    # Add children
    diagram.append("")
    for i, child in enumerate(child_details):
        diagram.append(f'class "{child["name"]}" as C{i} #pink {{')
        birth_date = child['birth_date'] if child['birth_date'] else "?"
        birth_place = child['birth_place'] if child['birth_place'] else "?"
        death_date = child['death_date'] if child['death_date'] else "?"
        death_place = child['death_place'] if child['death_place'] else "?"
        diagram.append(f'<&plus> {birth_date} {birth_place}')
        diagram.append(f'<&x> {death_date} {death_place}')
        diagram.append("}")
    
    # Add relationships
    if len(parents) == 2:
        diagram.append(f'\nP0 -- M1')
        diagram.append(f'P1 -- M1')
        diagram.append(f'M1 -- {xref_id.strip("@")}')
        
    if spouse:
        diagram.append(f'{xref_id.strip("@")} -- M2')
        diagram.append(f'S1 -- M2')
        
    for i in range(len(children)):
        if spouse:
            diagram.append(f'M2 -- C{i}')
        else:
            diagram.append(f'{xref_id.strip("@")} -- C{i}')
        
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

        print(create_individual_diagram(transmission, args.id))

# Example usage
if __name__ == '__main__':
    main(sys.argv)
