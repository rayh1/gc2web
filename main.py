import sys
from GedcomParser import GedcomParser
from typing import List

def main(argv: List[str]):
    gedcom_file_path = argv[1]
    with open(gedcom_file_path, 'r') as gedcom_stream:
        parser = GedcomParser()
        transmission = parser.parse(gedcom_stream)
        for gedcom_line in transmission.main_lines:
            gedcom_line.print()

# Example usage
if __name__ == '__main__':
    main(sys.argv)
