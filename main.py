import sys
from GedcomParser import GedcomParser

def main(argv):
    gedcom_file_path = argv[1]
    with open(gedcom_file_path, 'r') as gedcom_stream:
        parser = GedcomParser(gedcom_stream)
        parsed_lines = parser.parse()
        for gedcom_line in parser.lines:
            print(gedcom_line)

# Example usage
if __name__ == '__main__':
    main(sys.argv)
