import argparse
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

PLANTUML_BASE_URL: str = "https://www.plantuml.com/plantuml/svg"
CONTENT_DIR: Path = Path("/workspaces/gc2web/website/src/content/blog")

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

            content.append(f"# {individual.name}")

            content.append(f"![test]({PLANTUML_BASE_URL}/{PlantUMLEncoder.encode(PlantUMLCreator.create_individual_diagram(individual))})")

            content.append(f"## Gegevens")
            content.append(f"- Geboren op {individual.birth.date} te {individual.birth.place}")
            if individual.baptism.date.value or individual.baptism.place.value: content.append(f"- Gedoopt op {individual.baptism.date} te {individual.baptism.place}")
            content.append(f"- Overleden op {individual.death.date} te {individual.death.place}")
            if individual.burial.date.value or individual.burial.place.value: content.append(f"- Begraven op {individual.burial.date} te {individual.burial.place}")
            if len(individual.names)  > 1:
                content.append(f"- Alternatieve Namen")
                for name in individual.names[1:]:
                    content.append(f"  - {name}")

            content.append(f"## Ouders")
            father: Individual | None = individual.father
            if father:
                content.append(f"- De vader is [{father.name}](../{father.xref_id.lower()}/)")
            mother: Individual | None = individual.mother
            if mother:
                content.append(f"- De moeder is [{mother.name}](../{mother.xref_id.lower()}/)")

            content.append("")
            content.append(f"## Relaties en Kinderen")

            for fams in individual.fams:
                spouse: Individual | None = fams.spouse(individual)
                if spouse:
                    content.append(f"")
                    content.append(f"Gehuwd met [{spouse.name}](../{spouse.xref_id.lower()}/) op {fams.marriage.date} te {fams.marriage.place}")
                for child in fams.children:
                    content.append(f"- Kind [{child.name}](../{child.xref_id.lower()}/)")

            content.append(f"## Bronnen")
            for source in individual.sources:
                content.append(f"- [{source.title}](../{source.xref_id.lower()}/)")

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

            content.append(f"# {source.title}")
            content.append(f"")
            content.append(f"## Links")
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

