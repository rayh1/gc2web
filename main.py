import re
import sys
from GedcomParser import GedcomParser
from typing import List

def main(argv: List[str]):
    gedcom_file_path = argv[1]
    with open(gedcom_file_path, 'r') as gedcom_stream:
        parser = GedcomParser()
        transmission = parser.parse(gedcom_stream)

        tag = argv[2] if len(argv) > 2 else None
        value_re=argv[3] if len(argv) > 3 else None
        iterator = transmission.iterate(tag = tag, value_re=value_re)
        for line in iterator:
            print(line)

# Example usage
if __name__ == '__main__':
    main(sys.argv)
