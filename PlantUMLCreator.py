from typing import List
from Individual import Individual
from Family import Family
from Date import Date

# Constants
COLOR_MALE = '#E3F5FB'
COLOR_FEMALE = '#FBE3E3'
COLOR_UNKNOWN = '#lightgrey'
COLOR_MARRIAGE = '#lightyellow'
ICON_BIRTH = '<:baby_bottle:>'
ICON_DEATH = '<:skull_and_crossbones:>'
ICON_MARRIAGE = '<:wedding:>'
START_PLANTUML = [
    "@startuml",
    "skinparam backgroundColor transparent",
    "skinparam roundcorner 20",
    "hide circle",
    "hide empty members",
    "hide stereotype",
    "",
    "skinparam class {",
    "   BorderThickness<<main>> 3",
    "}",
    "",
    "' Parents",
]

END_PLANTUML = ["", "@enduml"]

def s(value) -> str:
    return str(value) if value else "?"

def add_individual_to_diagram(diagram: List[str], individual: Individual, color: str | None = None, stereotype: str | None = None):
    if color is None:
        if individual.is_male:
            color = COLOR_MALE
        elif individual.is_female:
            color = COLOR_FEMALE
        else:
            color = COLOR_UNKNOWN
    stereotype = f'<<{stereotype}>>' if stereotype else ''
    diagram.append(f'class "{individual.name}" as {individual.xref_id} {stereotype} {color} {{')
    
    birth_date = s(individual.birth.date) if individual.birth.date.value else s(individual.baptism.date)
    birth_place = s(individual.birth.place) if individual.birth.place else s(individual.baptism.place)
    diagram.append(f'{{field}} {ICON_BIRTH} {birth_date} {birth_place}')
    
    death_date = s(individual.death.date) if individual.death.date.value else s(individual.burial.date)
    death_place = s(individual.death.place) if individual.death.place else s(individual.burial.place)
    diagram.append(f'{{field}} {ICON_DEATH} {death_date} {death_place}')
    
    diagram.append("}")

def add_marriage_to_diagram(diagram: List[str], family: Family, color: str | None = None):
    if color is None:
        color = COLOR_MARRIAGE
    diagram.append(f'class "{ICON_MARRIAGE} {s(family.marriage.date)}" as {family.xref_id} {color} {{')
    diagram.append("}")

def create_individual_diagram(person: Individual) -> str:
    """Create a PlantUML family diagram for an individual"""    
    diagram = START_PLANTUML.copy()

    # Add parents
    family = person.famc
    if family:
        add_individual_to_diagram(diagram, family.husband)
        add_individual_to_diagram(diagram, family.wife)

        add_marriage_to_diagram(diagram, family)

        diagram.append(f'{family.husband.xref_id} -- {family.xref_id}')
        diagram.append(f'{family.wife.xref_id} -- {family.xref_id}')
        diagram.append(f'{family.xref_id} -- {person.xref_id}')

    # Add main individual
    diagram.append("")
    add_individual_to_diagram(diagram, person, stereotype="main")

    # Add spouse and children
    for family in person.fams:
        spouse: Individual | None = family.spouse(person)
        if not spouse:
            raise ValueError(f"Spuse not found for family {family.xref_id}")

        diagram.append("")
        add_individual_to_diagram(diagram, spouse)

        add_marriage_to_diagram(diagram, family)

        for i, child in enumerate(family.children):
            add_individual_to_diagram(diagram, child)

        # Add relationships
        diagram.append(f'{person.xref_id} -- {family.xref_id}')
        diagram.append(f'{spouse.xref_id} -- {family.xref_id}')
        for child in family.children:
            diagram.append(f'{family.xref_id} - {child.xref_id}')

        prev_child = None    
        for child in family.children:
            if prev_child:
                diagram.append(f'{prev_child.xref_id} -[hidden]- {child.xref_id}')
            prev_child = child

    diagram.extend(END_PLANTUML)
    return "\n".join(diagram)
