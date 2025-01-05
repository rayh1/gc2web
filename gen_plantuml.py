import PlantUMLCreator
import argparse
import sys

from typing import List
from GedcomParser import GedcomParser
from GedcomTransmission import GedcomTransmission
from Individual import Individual

def main(argv: List[str]):
    ap = argparse.ArgumentParser(description='Process a GEDCOM file.')
    ap.add_argument('file', type=str, help='Path to the GEDCOM file')
    ap.add_argument('-i', '--id', type=str, required=False, nargs='?', default=None, help='Id of Gedcom line')
    
    args = ap.parse_args(argv[1:])

    with open(args.file, 'r') as gedcom_stream:
        parser = GedcomParser()
        transmission: GedcomTransmission = parser.parse(gedcom_stream)
        transmission.parse_gedcom()

        individual: Individual | None = transmission.get_individual(args.id)
        if not individual:
            raise ValueError(f"Individual {args.id} not found")

        print(PlantUMLCreator.create_individual_diagram(individual))

# Example usage
if __name__ == '__main__':
    main(sys.argv)
