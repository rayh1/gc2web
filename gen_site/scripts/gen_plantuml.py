from typing import List

import argparse
import sys

from parser.GedcomParser import GedcomParser

from model.GedcomTransmission import GedcomTransmission
from model.Individual import Individual

import util.PlantUMLCreator as PlantUMLCreator

def main(argv: List[str]):
    ap = argparse.ArgumentParser(description='Process a GEDCOM file.')
    ap.add_argument('file', type=str, help='Path to the GEDCOM file')
    ap.add_argument('-i', '--id', type=str, required=False, nargs='?', default=None, help='Id of Gedcom line')
    
    args = ap.parse_args(argv[1:])

    with open(args.file, 'r') as gedcom_stream:
        GedcomParser().parse(gedcom_stream)
        GedcomTransmission().parse_gedcom()

        individual: Individual | None = GedcomTransmission().get_individual(args.id)
        if not individual:
            raise ValueError(f"Individual {args.id} not found")

        print(PlantUMLCreator.create_individual_diagram(individual))

# Example usage
if __name__ == '__main__':
    main(sys.argv)
