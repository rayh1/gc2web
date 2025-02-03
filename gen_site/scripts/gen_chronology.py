from datetime import datetime
import argparse
import sys

from parser.GedcomParser import GedcomParser

from model.GedcomTransmission import GedcomTransmission
from model.EventDetail import EventDetail

class ChronologyEvent:
    def __init__(self, event: EventDetail, description: str):
        self.event: EventDetail = event
        d = event.date.date()
        if not d:
            d = datetime.min
        self.date: datetime = d
        self.description = description

    def __lt__(self, other: 'ChronologyEvent'):
        return self.date < other.date

    def __str__(self):
        return f"[{self.description}] happens on {self.date}"

# https://mambaui.com/components/timeline
# https://flyonui.com/docs/components/timeline/
# https://daisyui.com/components/timeline/
def gen_chronology(individual_id: str):
    individual = GedcomTransmission().get_individual(individual_id)
    if individual is None:
        print(f"Individual with id {individual_id} not found")
        return

    events: list[ChronologyEvent] = []
    if individual.birth:
        events.append(ChronologyEvent(individual.birth, "Geboren"))
    if individual.death:
        events.append(ChronologyEvent(individual.death, "Overleden"))
    for family in individual.fams:
        if family.marriage:
            events.append(ChronologyEvent(family.marriage, f"Getrouwd met {family.spouse(individual).name}"))
            for child in family.children:
                if child.birth:
                    events.append(ChronologyEvent(child.birth, f"Kind {child.name}"))

    events.sort()

    HEADER = '<section class="dark:bg-gray-100 dark:text-gray-800">' \
    '<div class="container max-w-5xl px-4 py-12 mx-auto">' \
        '<div class="grid gap-4 mx-4 sm:grid-cols-12">' \
            '<div class="relative col-span-12 px-4 space-y-6 sm:col-span-9">' \
                '<div class="col-span-12 space-y-12 relative px-4 sm:col-span-8 sm:space-y-8 sm:before:absolute sm:before:top-2 sm:before:bottom-0 sm:before:w-0.5 sm:before:-left-3 before:dark:bg-gray-300">'
    print(HEADER)

    for event in events:
        print(					'<div class="flex flex-col sm:relative sm:before:absolute sm:before:top-2 sm:before:w-4 sm:before:h-4 sm:before:rounded-full sm:before:left-[-35px] sm:before:z-[1] before:dark:bg-gray-600"> ' \
						'<h3 class="text-xl font-semibold tracking-wide">' + event.description + '</h3>' \
						'<time class="text-xs tracking-wide uppercase dark:text-gray-600">'+ str(event.date) + '</time>' \
					'</div>')

    FOOTER = '                </div>' \
            '</div>' \
        '</div>' \
    '</div>' \
'</section>'
    print(FOOTER)    

def main(argv):
    ap = argparse.ArgumentParser(description='Set witness IDs in a GEDCOM file.')
    ap.add_argument('file', type=str, help='Path to the GEDCOM file')
    ap.add_argument('individual', type=str, help='Id of the individual')
    
    args = ap.parse_args(argv[1:])
    GedcomTransmission().parse_file(args.file)
    gen_chronology(args.individual)

if __name__ == '__main__':
    main(sys.argv)

