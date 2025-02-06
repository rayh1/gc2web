import argparse
import re
import sys

from parser.GedcomParser import GedcomParser

from model.GedcomModel import GedcomModel
from model.Individual import Individual
from model.Witness import Witness

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
    print(f"{witness.line_num} {witness.name} {individual.xref_id}")
    #print(f"{witness.line.line_num} {witness.name} {witness.relation}: xref_id={individual.xref_id}")
    #print(f"[{individual.name}] {witness.relation}: {individual.father.name}/{witness.name}")

def process_witnesses():
    for individual in GedcomModel().individuals:
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

def is_identified_witness2(witness: Witness) -> bool:
    return witness.xref_id != None or witness.relation == None

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

def is_zoon2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["zoon"])

def find_child2(name: str | None, individual: Individual) -> list[Individual]:
    results: list[Individual] = []
    if not name:
        return results
    for spouse in individual.spouses:
        for child in individual.children(spouse):
            if child.has_name(name):
                results.append(child)
    return results

### Dochter

def is_dochter2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["dochter"])

#### Father
def is_father2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["vader"])

def find_father2(individual: Individual) -> list[Individual]:
    results: list[Individual] = []
    father: Individual | None = individual.father
    if father:
        results.append(father)

    return results

#### Mother
def is_mother2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["moeder"])

def find_mother2(individual: Individual) -> list[Individual]:
    results: list[Individual] = []
    mother: Individual | None = individual.mother
    if mother:
        results.append(mother)

    return results

#### Sibling
def is_sibling2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["broer", "zus", "broeder", "zuster"])

def find_sibling2(name: str | None, individual: Individual) -> list[Individual]:
    results: list[Individual] = []
    if not name:
        return results
    for sibling in individual.siblings():
        if sibling.has_name(name):
            results.append(sibling)
    return results

#### Echtgenoot
def is_echtgenoot2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["echtgenoot"])

def find_echtgenoot2(name: str | None, individual: Individual) -> list[Individual]:
    results: list[Individual] = []
    if not name:
        return results
    for spouse in individual.spouses:
        if spouse.has_name(name):
            results.append(spouse)

    return results

#### Grandfather
def is_grandfather2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["grootvader"])

def find_grandfather2(name: str | None, individual: Individual) -> list[Individual]:
    results: list[Individual] = []
    if not name:
        return results

    if individual.father and individual.father.father and individual.father.father.has_name(name): 
        results.append(individual.father.father)
    
    if individual.mother and individual.mother.father and individual.mother.father.has_name(name): 
        results.append(individual.mother.father)

    return results

#### Grandmother
def is_grandmother2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["grootmoeder", "oma"])

def find_grandmother2(name: str | None, individual: Individual) -> list[Individual]:
    results: list[Individual] = []
    if not name:
        return results

    if individual.father and individual.father.mother and individual.father.mother.has_name(name): 
        results.append(individual.father.mother)
    
    if individual.mother and individual.mother.mother and individual.mother.mother.has_name(name): 
        results.append(individual.mother.mother)

    return results

#### Uncle
def is_uncle2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["oom"])

def find_uncle2(name: str | None, individual: Individual) -> list[Individual]:
    results: list[Individual] = []
    if not name:
        return results
    
    for ua in individual.uncles_aunts():
        if ua.has_name(name):
            results.append(ua)

    return results

#### Father Groom
def is_father_groom2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["vader bruidegom", 
                                                "vader van bruidegom", 
                                                "vader der bruidegom", 
                                                "vader van de bruidegom", 
                                                "vader echtgenoot", 
                                                "vader van de echtgenoot", 
                                                "vader der echtgenoot"])

#### Father Bride

def is_father_bride2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["vader bruid", 
                                                "vader van bruid", 
                                                "vader der bruid", 
                                                "vader echtgenote", 
                                                "vader van de echtgenoote", 
                                                "vader echtgenoote", 
                                                "vader van de bruid"])

#### Mother Groom
#moeder bruidegom
#moeder der bruidegom
#moeder van bruidegom
#moeder van den bruidegom
#moeder bruideg
#moeder echtgenoot
#moeder van de echtgenoot
#moeder van de bruidegom

def is_mother_groom2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["moeder bruidegom", 
                                                "moeder van bruidegom", 
                                                "moeder der bruidegom", 
                                                "moeder van bruidegom", 
                                                "moeder van den bruidegom", 
                                                "moeder bruideg", 
                                                "moeder echtgenoot", 
                                                "moeder van de echtgenoot", 
                                                "moeder van de bruidegom"])

#### Mother Bride
#moeder bruid
#moeder van bruid
#moeder der bruid
#moeder van de bruid
#moeder van den bruid
#moeder echtgenote
#moeder van de echtgenoote
#moeder echtgenoote

def is_mother_bride2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["moeder bruid", 
                                                "moeder van bruid", 
                                                "moeder der bruid", 
                                                "moeder van de bruid", 
                                                "moeder van den bruid", 
                                                "moeder echtgenote", 
                                                "moeder van de echtgenoote", 
                                                "moeder echtgenoote"])

#### Brother Groom
#broeder van den bruidegom
#broeder bruidegom
#broer van bruidegom
#broer der bruidegom
#broeder van de bruidegom
#broeder van den echtgenoot
#broeder des echtgenoots

def is_brother_groom2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["broeder van den bruidegom", 
                                                "broeder bruidegom", 
                                                "broer van bruidegom", 
                                                "broer der bruidegom", 
                                                "broeder van de bruidegom", 
                                                "broeder van den echtgenoot", 
                                                "broeder des echtgenoots"])

#### Brother Bride
#broeder van de echtgenoote
#broeder der bruid
#broeder van den bruid
#broer der bruid
#broeder van den echtgenoote
#broeder van de bruid

def is_brother_bride2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["broeder van de echtgenoote", 
                                                "broeder der bruid", 
                                                "broeder van den bruid", 
                                                "broer der bruid", 
                                                "broeder van den echtgenoote", 
                                                "broeder van de bruid"])

#### Uncle Groom
#oom van de bruidegom
#oom van den echtgenoot
#oom echtgenoot

def is_uncle_groom2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["oom van de bruidegom", 
                                                "oom van den echtgenoot", 
                                                "oom echtgenoot"])

#### Uncle Bride
#oom van de echtgenoote
#oom der bruid
#oom van den echtgenoote

def is_uncle_bride2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["oom van de echtgenoote", 
                                                "oom der bruid", 
                                                "oom van den echtgenoote"])

#### Brother-in-law
#zwager van den echtgenoot
#zwager der bruidegom
#zwager van bruidegom
#behuwdneef van den echtgenoot
#zwager van de echtgenoote
#zwager der bruid
#schoonbroeder van de echtgenoote
#schoonbroeder

def is_brother_in_law2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["zwager van den echtgenoot", 
                                                "zwager der bruidegom", 
                                                "zwager van bruidegom", 
                                                "behuwdneef van den echtgenoot", 
                                                "zwager van de echtgenoote", 
                                                "zwager der bruid", 
                                                "schoonbroeder van de echtgenoote", 
                                                "schoonbroeder"])

def find_brother_in_law2(name: str | None, individual: Individual) -> list[Individual]:
    results: list[Individual] = []
    if not name:
        return results
    for sibling in individual.siblings():
        for spouse in sibling.spouses:
            if spouse.has_name(name):
                results.append(spouse)
    return results

#### Something
#voogd van bruidegom
#toeziend voogd van bruidegom
#toeziende voogd bruid
#voogd bruid
#bekende der bruid
#bloedverwant in den tweeden graad zijdlinie van den eersten echtgenoot
#bloedverwant in den tweeden graad zijdlinie der tweeden echtgenoot
#bloedverwant in den vierden graad zijdlinie van den eersten echtgenoot
#aangehuwde in den eersten graad nederdalende linie der tweede echtgenoot
#aangehuwde in den tweeden graad zijdlinie der tweede echtgenoot
#bloedverwant in dentweede graad zijdlinieder tweede echtgenoot
#stiefvader van de echtgenoote

def is_something_of_groom2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["voogd van bruidegom", 
                                                "toeziend voogd van bruidegom", 
                                                "bloedverwant in den tweeden graad zijdlinie van den eersten echtgenoot", 
                                                "bloedverwant in den vierden graad zijdlinie van den eersten echtgenoot"])

def is_something_of_bride2(witness: Witness) -> bool:
    return has_exact_phrases(witness.relation, ["toeziende voogd bruid", 
                                                "voogd bruid", 
                                                "bekende der bruid", 
                                                "bloedverwant in den tweeden graad zijdlinie der tweeden echtgenoot", 
                                                "aangehuwde in den eersten graad nederdalende linie der tweede echtgenoot", 
                                                "aangehuwde in den tweeden graad zijdlinie der tweede echtgenoot", 
                                                "bloedverwant in dentweede graad zijdlinieder tweede echtgenoot", 
                                                "stiefvader van de echtgenoote"])

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

def print_witnesses(witness: Witness, individuals: list[Individual], individual: Individual):
    #print(f"{witness.line_num} {witness.name} {show_candidates(individuals)}")
    print(f"{witness.line_num} {witness.relation}: {witness.name} = {show_candidates_names(individuals)} --> {individual.name} {individual.xref_id}")

def identify_witnesses():
    for individual in GedcomModel().individuals:
        for event in [individual.birth, individual.baptism, individual.death, individual.burial]:
            for witness in event.witnesses:

                if is_identified_witness2(witness):
                   continue

                if is_uncle2(witness):
                    candidates: list[Individual] = find_uncle2(witness.name, individual)
                    print_witnesses(witness, candidates, individual)
                
                if is_grandmother2(witness):
                    candidates: list[Individual] = find_grandmother2(witness.name, individual)
                    print_witnesses(witness, candidates, individual)

        for fams in individual.fams:
            for witness in fams.marriage.witnesses:

                if is_identified_witness2(witness):
                   continue

                if is_father_groom2(witness):
                    candidates: list[Individual] = find_father2(fams.husband)
                    print_witnesses(witness, candidates, fams.husband)

                if is_father_bride2(witness):
                    candidates: list[Individual] = find_father2(fams.wife)
                    print_witnesses(witness, candidates, fams.wife)

                if is_mother_groom2(witness):
                    candidates: list[Individual] = find_mother2(fams.husband)
                    print_witnesses(witness, candidates, fams.husband)

                if is_mother_bride2(witness):
                    candidates: list[Individual] = find_mother2(fams.wife)
                    print_witnesses(witness, candidates, fams.wife)

                if is_brother_groom2(witness):
                    candidates: list[Individual] = find_sibling2(witness.name, fams.husband)
                    print_witnesses(witness, candidates, fams.husband)

                if is_brother_bride2(witness):
                    candidates: list[Individual] = find_sibling2(witness.name, fams.wife)
                    print_witnesses(witness, candidates, fams.wife)

                if is_uncle_groom2(witness):
                    candidates: list[Individual] = find_uncle2(witness.name, fams.husband)
                    print_witnesses(witness, candidates, fams.husband)

                if is_uncle_bride2(witness):
                    candidates: list[Individual] = find_uncle2(witness.name, fams.wife)
                    print_witnesses(witness, candidates, fams.wife)

                if is_brother_in_law2(witness):
                    candidates: list[Individual] = find_brother_in_law2(witness.name, fams.husband)
                    print_witnesses(witness, candidates, fams.husband)

                if is_brother_in_law2(witness):
                    candidates: list[Individual] = find_brother_in_law2(witness.name, fams.husband)
                    print_witnesses(witness, candidates, fams.wife)

                if is_something_of_groom2(witness):
                    print_witnesses(witness, [], fams.husband)

                if is_something_of_bride2(witness):
                    print_witnesses(witness, [], fams.wife)

def main(argv):
    ap = argparse.ArgumentParser(description='Set witness IDs in a GEDCOM file.')
    ap.add_argument('file', type=str, help='Path to the GEDCOM file')
    
    args = ap.parse_args(argv[1:])
    GedcomModel().parse_file(args.file)
    identify_witnesses()

if __name__ == '__main__':
    main(sys.argv)
