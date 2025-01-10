import argparse
from datetime import datetime
import sys
import logging
from pathlib import Path
from typing import List
from tqdm import tqdm

import PlantUMLEncoder
import PlantUMLCreator
from GedcomTransmission import GedcomTransmission
from GedcomParser import GedcomParser
from Individual import Individual
from SourcesMixin import SourcesMixin
from Source import Source
from EventDetails import EventDetails

PLANTUML_BASE_URL: str = "https://www.plantuml.com/plantuml/svg"
CONTENT_DIR: Path = Path("/workspaces/gc2web/website/src/content/blog")
LINK_ICON: str = ":link:"
HEADER_PREFIX: str = "###"

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def s(value) -> str:
    return str(value) if value else "?"

def individual_url(individual: Individual) -> str:
    return f"../{individual.xref_id.lower()}/"

def source_url(source: Source) -> str:
    return f"../{source.xref_id.lower()}/"

def individual_link(individual: Individual) -> str:
    return f"[{individual.name}]({individual_url(individual)})"

def source_link(source: Source) -> str:
    return f"[{source.title}]({source_url(source)})"

def sources_annotation(sources: SourcesMixin | None) -> str:
    if not sources or len(sources.sources) == 0: return ""
    
    result = "<sup>"
    for source in sources.sources:
        result += f"<a href=\"{source_url(source)}\" style=\"text-decoration:none\" title=\"{source.title}\">{LINK_ICON}</a>"
    return result + "</sup>"

def age_str(individual: Individual, event: EventDetails) -> str:
    return f"oud {s(individual.age(event.date))} jaar"

def generate_individual_page(individual: Individual, filepath: Path):
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as file:
            content = []
            content.append(f"---")
            content.append(f"title: \"{individual.name}\"")
            content.append(f"description: \"Individual\"")
            content.append(f"pubDate: \"November 20 2024\"")
            content.append(f"---")
            content.append(f"")

            content.append(f"{HEADER_PREFIX} Boom")
            content.append("<details><summary>Toon</summary>")
            content.append(f"")
            content.append(f"![test]({PLANTUML_BASE_URL}/{PlantUMLEncoder.encode(PlantUMLCreator.create_individual_diagram(individual))})")
            content.append("</details>")
            content.append(f"")

            content.append(f"{HEADER_PREFIX} Gegevens")
            content.append(f"- Naam: {individual.name} {sources_annotation(individual.name)}")
            content.append(f"- Geboren op {individual.birth.date} te {individual.birth.place} {sources_annotation(individual.birth)}")
            if individual.baptism.date.value or individual.baptism.place.value: content.append(f"- Gedoopt op {individual.baptism.date} te {individual.baptism.place} {sources_annotation(individual.baptism)}")
            content.append(f"- Overleden op {individual.death.date} te {individual.death.place}, {age_str(individual, individual.end_life)} jaar {sources_annotation(individual.death)}")
            if individual.burial.date.value or individual.burial.place.value: content.append(f"- Begraven op {individual.burial.date} te {individual.burial.place} {sources_annotation(individual.burial)}")
            if len(individual.names)  > 1:
                content.append(f"- Alternatieve namen:")
                for name in individual.names[1:]:
                    content.append(f"  - {name} {sources_annotation(name)}")

            if individual.occupations:
                content.append(f"{HEADER_PREFIX} Beroepen")
                sorted_occupations = sorted(individual.occupations, key=lambda x: x.date.date() or datetime.min)
                for occupation in sorted_occupations:
                    content.append(f"- {occupation.value} op {occupation.date} te {occupation.place}, {age_str(individual, occupation)} {sources_annotation(occupation)}")

            if individual.locations():
                content.append(f"{HEADER_PREFIX} Verblijfplaatsen")
                for location in individual.locations():
                    extra_info = ""
                    if location.family:
                        extra_info = f"met ouders"
                    elif location.spouse:
                        extra_info = f"met {individual_link(location.spouse)}"
                    content.append(f"- {location.event.place} {location.event.address if location.event.address else ""} op {location.event.date}, {age_str(individual, location.event)} {extra_info} {sources_annotation(location.event)}")

            content.append(f"{HEADER_PREFIX} Ouders")
            father: Individual | None = individual.father
            if father:
                content.append(f"- De vader is {individual_link(father)}")
            mother: Individual | None = individual.mother
            if mother:
                content.append(f"- De moeder is {individual_link(mother)}")

            content.append("")
            content.append(f"{HEADER_PREFIX} Relaties en Kinderen")

            for fams in individual.fams:
                spouse: Individual | None = fams.spouse(individual)
                if spouse:
                    content.append(f"")
                    content.append(f"Gehuwd met {individual_link(spouse)} ({age_str(spouse, fams.marriage)}) op {fams.marriage.date} te {fams.marriage.place}, {age_str(individual, fams.marriage)} {sources_annotation(fams.marriage)}")
                for child in fams.children:
                    content.append(f"- Kind {individual_link(child)}")

            content.append(f"{HEADER_PREFIX} Bronnen lijst")
            for source in individual.sources:
                content.append(f"- {source_link(source)}")

            file.writelines("\n".join(content))
    except IOError as e:
        logger.error(f"Failed to write file {filepath}: {e}")
        raise

def generate_source_page(source, filepath):
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as file:
            content = []
            content.append(f"---")
            content.append(f"title: \"{source.title}\"")
            content.append(f"description: \"Source\"")
            content.append(f"pubDate: \"November 20 2024\"")
            content.append(f"---")
            content.append(f"")

            if source.repository:
                content.append(f"{HEADER_PREFIX} Archief")
                content.append(f"[{source.repository.name}]({source.repository.www})")
                content.append(f"")

            content.append(f"{HEADER_PREFIX} Rechtstreekse Verwijzingen")
            for publication in source.publications:
                content.append(f"- {publication}")

            file.writelines("\n".join(content))
    except IOError as e:
        logger.error(f"Failed to write file {filepath}: {e}")
        raise        

def generate_individual_pages(transmission: GedcomTransmission, output_dir: Path):
    logger.info(f"Generating pages for {len(transmission.individuals)} individuals")
    
    for individual in tqdm(transmission.individuals, desc="Generating individual pages"):
        generate_individual_page(individual, output_dir / f"{individual.xref_id}.md")

    logger.info(f"Successfully generated {len(transmission.individuals)} individual pages")

def generate_source_pages(transmission: GedcomTransmission, output_dir: Path):
    logger.info(f"Generating pages for {len(transmission.sources)} sources")
    
    for source in tqdm(transmission.sources, desc="Generating source pages"):
        generate_source_page(source, output_dir / f"{source.xref_id}.md")

    logger.info(f"Successfully generated {len(transmission.sources)} source pages")

def main(argv: List[str]):
    ap = argparse.ArgumentParser(description='Process a GEDCOM file.')
    ap.add_argument('file', type=str, help='Path to the GEDCOM file')
    
    args = ap.parse_args(argv[1:])

    with open(args.file, 'r') as gedcom_stream:
        parser = GedcomParser()
        transmission = parser.parse(gedcom_stream)
        transmission.parse_gedcom()
    
    generate_individual_pages(transmission, CONTENT_DIR)
    generate_source_pages(transmission, CONTENT_DIR)

# Example usage
if __name__ == '__main__':
    main(sys.argv)

