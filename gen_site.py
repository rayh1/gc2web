import argparse
import os
import sys
from typing import List
from GedcomTransmission import GedcomTransmission
from GedcomParser import GedcomParser
from Individual import Individual

def generate_markdown_files(transmission: GedcomTransmission, output_dir: str):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for i, individual in enumerate(transmission.individuals.values()):
        #if i >= 3:
        #    break
        filename = f"{individual.xref_id}.md"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as file:
            content = []
            content.append(f"---")
            content.append(f"title: \"{individual.name}\"")
            #content.append(f"tags: [\"en\", \"tech\"]")
            content.append(f"description: \"Individual\"")
            content.append(f"pubDate: \"November 20 2024\"")
            #content.append(f"draft: false\n")
            content.append(f"---")
            content.append(f"")
            content.append(f"# {individual.name}")

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

