import re
import sys
import argparse
from GedcomParser import GedcomParser
from typing import List

def main(argv: List[str]):
    ap = argparse.ArgumentParser(description='Process a GEDCOM file.')
    ap.add_argument('file', type=str, help='Path to the GEDCOM file')
    ap.add_argument('-i', '--id', type=str, required=False, nargs='?', default=None, help='Id of Gedcom line')
    ap.add_argument('-t', '--tag', type=str, required=False, nargs='?', default=None, help='Tag to filter by')
    ap.add_argument('-v', '--value',  type=str, required=False, nargs='?', default=None, help='Regex to filter values by')
    ap.add_argument('--no-follow-pointer', action='store_true', help='Do not follow pointers')
    
    args = ap.parse_args(argv[1:])

    with open(args.file, 'r') as gedcom_stream:
        parser = GedcomParser()
        transmission = parser.parse(gedcom_stream)

        follow_pointer: bool = not args.no_follow_pointer

        if args.id:
            iterator = transmission.iterate_id(id = args.id, tag = args.tag, value_re=args.value, follow_pointers=follow_pointer)
        else:
            iterator = transmission.iterate(line = None, tag = args.tag, value_re=args.value, follow_pointers=follow_pointer)

        for line in iterator:
            print(line)

# Example usage
if __name__ == '__main__':
    main(sys.argv)
