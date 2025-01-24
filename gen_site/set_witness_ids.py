import argparse
import sys
from GedcomParser import GedcomParser
from GedcomTransmission import GedcomTransmission
from Individual import Individual
from Witness import Witness



def parse_gedom(gedcom_file: str):
    with open(gedcom_file, 'r') as gedcom_stream:
        parser = GedcomParser()
        transmission = parser.parse(gedcom_stream)
        transmission.parse_gedcom()

def is_father(witness: Witness, individual: Individual) -> bool:
    relation = (witness.relation or "").lower()
    if not individual.father:
        return False
    return "vader" in relation and "grootvader" not in relation and "peetvader" not in relation

def is_mother(witness: Witness, individual: Individual) -> bool:
    relation = (witness.relation or "").lower()
    if not individual.mother:
        return False
    return "moeder" in relation and "grootmoeder" not in relation and "peetmoeder" not in relation

def is_father_marriage(witness: Witness, individual: Individual) -> bool:
    relation = (witness.relation or "").lower()
    if not individual.father:
        return False
    if individual.is_male:
        return "vader van bruidegom" in relation
    elif individual.is_female:
        return "vader van bruid" in relation
    
    return False

def process_witnesses():
    for individual in GedcomTransmission().individuals:
        for event in [individual.birth, individual.baptism, individual.death, individual.burial]:
            for witness in event.witnesses:
                if is_father(witness, individual):
                    print(f"{witness.relation}: {individual.father.name}/{witness.name}")
                elif is_mother(witness, individual):
                    print(f"{witness.relation}: {individual.mother.name}/{witness.name}")

        for fams in individual.fams:
            for witness in fams.marriage.witnesses:
                if is_father_marriage(witness, individual):
                    print(f"{witness.relation}: {individual.father.name}/{witness.name}")

def main(argv):
    ap = argparse.ArgumentParser(description='Set witness IDs in a GEDCOM file.')
    ap.add_argument('file', type=str, help='Path to the GEDCOM file')
    
    args = ap.parse_args(argv[1:])
    parse_gedom(args.file)
    process_witnesses()

if __name__ == '__main__':
    main(sys.argv)
