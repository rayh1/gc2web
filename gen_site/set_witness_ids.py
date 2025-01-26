import argparse
import re
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

#def has_same_name(witness: Witness, individual: Individual) -> bool:
#    return witness.name == individual.name.value.replace("/", "")

def is_related(witness: Witness, individual: Individual, rels: list[str], excl:list[str]) -> bool:
    relation = (witness.relation or "").lower()
    for rel in rels:
        if rel in relation:
            for ex in excl:
                if ex in relation:
                    return False
            return True
    return False

def is_father(witness: Witness, individual: Individual) -> bool:
    #if not individual.father:
    #    return False
    return is_related(witness, individual, ["vader"], ["grootvader", "peetvader", "stiefvader"])

def is_mother(witness: Witness, individual: Individual) -> bool:
    #if not individual.mother:
    #    return False
    return is_related(witness, individual, ["moeder"], ["grootmoeder", "peetmoeder", "stiefmoeder"])

GROOM_RELATIONS = ["van de bruidegom", "van bruidegom", "bruidegom", "der bruidegom", "van de echtgenoot", "van echtgenoot", "echtgenoot", "der echtgenoot"]
BRIDE_RELATIONS = ["van de bruid", "van bruid", "bruid", "der bruid", "van de echtgenote", "van echtgenote", "echtgenote", "der echtgenote", "van de echtgenoote", "van echtgenoote", "echtgenoote", "der echtgenoote"]

def is_father_groom(witness: Witness, individual: Individual) -> bool:
    #if not individual.father:
    #    return False
    return is_related(witness, individual, ["vader " + r for r in GROOM_RELATIONS], ["grootvader", "peetvader", "stiefvader", "echtgenoote"])

def is_father_bride(witness: Witness, individual: Individual) -> bool:
    #if not individual.father:
    #    return False
    return is_related(witness, individual, ["vader " + r for r in BRIDE_RELATIONS], ["grootvader", "peetvader", "stiefvader", "bruidegom"])

def is_father_in_marriage(witness: Witness, individual: Individual) -> bool:
    if individual.is_male:
        return is_father_groom(witness, individual)
    elif individual.is_female:
        return is_father_bride(witness, individual)
                
    return False

def is_mother_groom(witness: Witness, individual: Individual) -> bool:
    #if not individual.mother:
    #    return False
    return is_related(witness, individual, ["moeder " + r for r in GROOM_RELATIONS], ["grootmoeder", "peetmoeder", "stiefmoeder", "echtgenoote"])

def is_mother_bride(witness: Witness, individual: Individual) -> bool:
    #if not individual.mother:
    #    return False
    return is_related(witness, individual, ["moeder " + r for r in BRIDE_RELATIONS], ["grootmoeder", "peetmoeder", "stiefmoeder", "bruidegom"])

def is_mother_in_marriage(witness: Witness, individual: Individual) -> bool:
    if individual.is_male:
        return is_mother_groom(witness, individual)
    elif individual.is_female:
        return is_mother_bride(witness, individual)
                
    return False

def print_witness(witness: Witness, individual: Individual):
    if witness.xref_id:
        return
    print(f"{witness.line.line_num} {witness.name} {individual.xref_id}")
    #print(f"{witness.line.line_num} {witness.name} {witness.relation}: xref_id={individual.xref_id}")
    #print(f"[{individual.name}] {witness.relation}: {individual.father.name}/{witness.name}")

def process_witnesses():
    for individual in GedcomTransmission().individuals:
        for event in [individual.birth, individual.baptism, individual.death, individual.burial]:
            for witness in event.witnesses:
                if is_father(witness, individual):
                    print_witness(witness, individual.father)
                elif is_mother(witness, individual):
                    print_witness(witness, individual.mother)

        for fams in individual.fams:
            for witness in fams.marriage.witnesses:
                if is_father_in_marriage(witness, individual):
                    print_witness(witness, individual.father)
                elif is_mother_in_marriage(witness, individual):
                    print_witness(witness, individual.mother)

def is_unknown_particular_witness(witness: Witness, individual: Individual) -> bool:
    if witness.xref_id or not witness.relation:
        return False

    if is_father(witness, individual) and not individual.father:
        return False
    if is_mother(witness, individual) and not individual.mother:
        return False
    
    return True

def is_unknown_marriage_witness(witness: Witness, individual: Individual) -> bool:
    if witness.xref_id or not witness.relation:
        return False

    if is_father_groom(witness, individual) and individual.is_male and not individual.father:
        return False
    if is_father_bride(witness, individual) and individual.is_female and not individual.father:
        return False
    if is_mother_groom(witness, individual) and individual.is_male and not individual.mother:
        return False
    if is_mother_bride(witness, individual) and individual.is_female and not individual.mother:
        return False

    if is_father_groom(witness, individual) and individual.is_female:
        return False
    if is_father_bride(witness, individual) and individual.is_male:
        return False
    if is_mother_groom(witness, individual) and individual.is_female:
        return False
    if is_mother_bride(witness, individual) and individual.is_male:
        return False
    
    return True

def has_exact_phrase(s: str | None, phrase: str) -> bool:
    if not s:
        return False
    # Add word boundaries around the phrase and make case insensitive
    pattern = r'\b' + re.escape(phrase) + r'\b'
    return bool(re.search(pattern, s, re.IGNORECASE))

def has_exact_phrases(s: str | None, phrases: list[str]) -> bool:
    if not s:
        return False
    for phrase in phrases:
        if has_exact_phrase(s, phrase):
            return True
    return False

#### Zoon

def is_zoon(witness: Witness, individual: Individual) -> bool:
    return has_exact_phrases(witness.relation, ["zoon"])

def find_zoon(name: str | None, individual: Individual) -> list[Individual]:
    results: list[Individual] = []
    if not name:
        return results
    for spouse in individual.spouses:
        for child in individual.children(spouse):
            if child.has_name(name):
                results.append(child)
    return results

def show_candidates_names(candidates: list[Individual]) -> str | list[str]:
    if len(candidates) == 0:
        return "GEEN"
    if len(candidates) == 1:
        return str(candidates[0].name)
    
    return [str(i.name) for i in candidates]

def show_candidates(candidates: list[Individual]) -> str | list[str]:
    if len(candidates) == 0:
        return "GEEN"
    if len(candidates) == 1:
        return candidates[0].xref_id
    
    return [i.xref_id for i in candidates]

def print_witnesses(witness: Witness, individuals: list[Individual]):
    if witness.xref_id:
        return
    print(f"{witness.line_num} {witness.name} {show_candidates(individuals)}")
    #print(f"{witness.line_num} {witness.relation}: {witness.name} {show_candidates_names(individuals)}")

def list_witnesses_relations():
    for individual in GedcomTransmission().individuals:
        for event in [individual.birth, individual.baptism, individual.death, individual.burial]:
            for witness in event.witnesses:
                if not is_unknown_particular_witness(witness, individual):
                    continue
                
                if is_zoon(witness, individual):
                    zonen: list[Individual] = find_zoon(witness.name, individual)
                    print_witnesses(witness, zonen)
                    #print(f"{witness.line_num} {witness.relation}: {witness.name} ({individual.name}) {show_candidates(zonen)}")

        # for fams in individual.fams:
        #     for witness in fams.marriage.witnesses:
        #         if is_unknown_marriage_witness(witness, individual):
        #             print(f"{witness.line_num} {witness.relation}: {witness.name} ({individual.name})")

def main(argv):
    ap = argparse.ArgumentParser(description='Set witness IDs in a GEDCOM file.')
    ap.add_argument('file', type=str, help='Path to the GEDCOM file')
    
    args = ap.parse_args(argv[1:])
    parse_gedom(args.file)
    #process_witnesses()
    list_witnesses_relations()

if __name__ == '__main__':
    main(sys.argv)
