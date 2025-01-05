from dataclasses import dataclass

@dataclass(frozen=True)
class GedcomTags:
    HEAD: str = "HEAD"
    SOUR: str = "SOUR"
    DEST: str = "DEST"
    SUBM: str = "SUBM"
    SUBN: str = "SUBN"
    GEDC: str = "GEDC"
    CHAR: str = "CHAR"
    INDI: str = "INDI"
    NAME: str = "NAME"
    SEX: str = "SEX"
    BIRT: str = "BIRT"
    DEAT: str = "DEAT"
    BURI: str = "BURI"
    RESI: str = "RESI"
    FAM: str = "FAM"
    FAMS: str = "FAMS"
    FAMC: str = "FAMC"
    ADOP: str = "ADOP"
    SLGC: str = "SLGC"
    MARR: str = "MARR"
    SLGS: str = "SLGS"
    HUSB: str = "HUSB"
    WIFE: str = "WIFE"
    CHIL: str = "CHIL"
    ADDR: str = "ADDR"
    PHON: str = "PHON"
    DATA: str = "DATA"
    EVEN: str = "EVEN"
    DATE: str = "DATE"
    PLAC: str = "PLAC"
    AGNC: str = "AGNC"
    TITL: str = "TITL"
    ABBR: str = "ABBR"
    REPO: str = "REPO"
    CALN: str = "CALN"
    MEDI: str = "MEDI"
    TRLR: str = "TRLR"
    CONC: str = "CONC"
    CONT: str = "CONT"
    CHR: str = "CHR"
