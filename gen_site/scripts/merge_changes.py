class Entry:
    def __init__(self, num, name, id):
        self.num = num
        self.name = name
        self.id = id

def read_entries(filepath):
    entries = []
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            if not line.strip():
                continue
            parts = line.split()
            num = int(parts[0])
            id = parts[-1]
            name = ' '.join(parts[1:-1])
            entries.append(Entry(num, name, id))
    return entries

def filter_entries(entries):
    seen = set()
    filtered = []
    for entry in entries:
        if entry.num not in seen:
            filtered.append(entry)
            seen.add(entry.num)
    return filtered

def read_gedcom_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.readlines()

def write_gedcom_file(filepath, lines):
    with open(filepath, 'w', encoding='utf-8') as file:
        file.writelines(lines)

def update_gedcom(entries, lines):
    for entry in reversed(entries):
        print (f"{entry.num}: {lines[entry.num]}")
        i = entry.num - 1
        for line in lines[entry.num - 1:]:
            if entry.name.strip() in line:
                lines.insert(i + 1, f"3 CONT     xref_id: {entry.id}\n")
                break
            i += 1

def main():
    entries = read_entries('/workspaces/gc2web/gen_site/changes.txt')
    filtered_entries = filter_entries(entries)
    sorted_entries = sorted(filtered_entries, key=lambda x: x.num)
    lines = read_gedcom_file('/workspaces/gc2web/gen_site/Hoofman.ged')
    update_gedcom(sorted_entries, lines)
    write_gedcom_file('/workspaces/gc2web/gen_site/Hoofman_updated.ged', lines)

if __name__ == "__main__":
    main()
