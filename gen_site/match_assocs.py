import argparse
import sys
from GedcomParser import GedcomParser
from GedcomTransmission import GedcomTransmission

def witnesses_to_string(witnesses):
    if len(witnesses) == 0:
        return ""
    return f"witnesses ({str(witnesses[0].line_num)}): " + ', '.join([witness.name + " (age=" + str(witness.age) + ")" for witness in witnesses])

def match_assocs():
# Loop through all individuals and all their associations
# For each association, find the corresponding event in the individual's events (this is based on the rel_type of the association)
# Then try to find a witness for that event that has the same value for the xref_id fiels as the individual in the association
# Then print an overview of the associations that do NOT have a matching witness
# To match associations to events use the following rules:
# association.rel_type == '@#INDI:BIRT@' -> event is individual.birth
# association.rel_type == '@#INDI:DEAT@' -> event is individual.death
# association.rel_type == '@#INDI:CHR@' -> event is individual.baptism
# If association.rel_type is not one of the above, just print the association and the individual it is associated with

    for individual in GedcomTransmission().individuals:
        if len(individual.associations) == 0:
            continue
        print("")
        print(f"{individual.name} ({individual.xref_id}) has {len(individual.associations)} associations")
        for association in individual.associations:
            if association.rel_type == '@#INDI:BIRT@':
                event = individual.birth
            elif association.rel_type == '@#INDI:DEAT@':
                event = individual.death
            elif association.rel_type == '@#INDI:CHR@':
                event = individual.baptism
            else:
                event = None
            if event:
                print(f"{association.rel_type} {association.rel_desc} {association.individual().name} (id={association.individual_id}, age={association.individual().age(event.date)}, line={association.line_num})")
                for witness in event.witnesses:
                    if witness.xref_id == association.individual_id:
                        # Check if the age of the witness matches the age of the individual in the association. They may differ by one year due to the way ages are calculated in the GEDCOM file
                        is_age_match = witness.age == association.individual().age(event.date) or witness.age == association.individual().age(event.date) + 1 or witness.age == association.individual().age(event.date) - 1
                        warning_age_match = "" if is_age_match else "XXX"
                        print(f"--> {warning_age_match}MATCH {witness.name} (id={witness.xref_id}, age={witness.age}, line={str(witness.line_num)})")
                        break
                else:
                    print(f"--> NO MATCH ({witnesses_to_string(event.witnesses)})")
            else:
                print(f"{association.rel_type} {association.rel_desc} {association.individual().name} (id={association.individual_id})")
                print(f"--> UNKNOWN EVENT")

def main(argv):
    ap = argparse.ArgumentParser(description='Set witness IDs in a GEDCOM file.')
    ap.add_argument('file', type=str, help='Path to the GEDCOM file')
    
    args = ap.parse_args(argv[1:])
    GedcomParser.parse_file(args.file)
    match_assocs()

if __name__ == '__main__':
    main(sys.argv)
