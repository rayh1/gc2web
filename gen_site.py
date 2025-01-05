import argparse
import os
import sys
import logging
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm

import PlantUMLEncoder
import PlantUMLCreator
from GedcomTransmission import GedcomTransmission
from GedcomParser import GedcomParser
from Individual import Individual

PLANTUML_BASE_URL = "https://www.plantuml.com/plantuml/svg"

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def write_markdown_file(individual: Individual, filepath: Path) -> None:
    """Write markdown content for an individual to a file.
    
    Args:
        individual: The Individual object containing genealogical data
        filepath: Path object for the output file
    """
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

            content.append(f"- Geboren op {individual.birth_date} te {individual.birth_place}")
            content.append(f"- Overleden op {individual.death_date} te {individual.death_place}")

            content.append(f"## Ouders")
            father: Individual | None = individual.father
            if father:
                content.append(f"- De vader is [{father.name}](../{father.xref_id.lower()}/)")
            mother: Individual | None = individual.mother
            if father:
                content.append(f"- De moeder is [{mother.name}](../{mother.xref_id.lower()}/)")

            content.append("")
            content.append(f"## Relaties en Kinderen")

            for fams in individual.fams:
                spouse: Individual | None = fams.spouse(individual)
                if spouse:
                    content.append(f"")
                    content.append(f"Gehuwd met [{spouse.name}](../{spouse.xref_id.lower()}/) op {fams.marriage_date} te {fams.marriage_place}")
                for child in fams.children:
                    content.append(f"- Kind [{child.name}](../{child.xref_id.lower()}/)")

            file.writelines("\n".join(content))
    except IOError as e:
        logger.error(f"Failed to write file {filepath}: {e}")
        raise

def generate_markdown_files(transmission: GedcomTransmission, 
                          output_dir: str) -> None:
    """Generate markdown files for all individuals in the transmission.
    
    Args:
        transmission: GedcomTransmission object containing all genealogical data
        output_dir: Directory path where markdown files will be created
    
    Raises:
        ValueError: If transmission is empty or output_dir is invalid
    """
    if not transmission.individuals:
        raise ValueError("No individuals found in transmission")
    
    output_path = Path(output_dir)
    if not output_path.parent.exists():
        raise ValueError(f"Parent directory {output_path.parent} does not exist")

    logger.info(f"Generating markdown files for {len(transmission.individuals)} individuals")
    
    for individual in tqdm(transmission.individuals.values(),
                         desc="Generating markdown files"):
        filename = f"{individual.xref_id}.md"
        filepath = output_path / filename
        write_markdown_file(individual, filepath)

    logger.info(f"Successfully generated {len(transmission.individuals)} files")

def main(argv: List[str]):
    ap = argparse.ArgumentParser(description='Process a GEDCOM file.')
    ap.add_argument('file', type=str, help='Path to the GEDCOM file')
    
    args = ap.parse_args(argv[1:])

    with open(args.file, 'r') as gedcom_stream:
        parser = GedcomParser()
        transmission = parser.parse(gedcom_stream)
        transmission.parse_gedcom()

    generate_markdown_files(transmission, "/workspaces/gc2web/website/src/content/blog")

# Example usage
if __name__ == '__main__':
    main(sys.argv)

