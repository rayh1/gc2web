import re

def replace_publ_with_note(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith('1 PUBL'):
            new_lines.append('1 NOTE ---\n')
            new_lines.append('2 CONT links:\n')
            while i < len(lines) and (lines[i].startswith('1 PUBL') or lines[i].startswith('2 CONT')):
                if lines[i].startswith('1 PUBL'):
                    new_lines.append(f'2 CONT   -  {lines[i][7:]}')
                elif lines[i].startswith('2 CONT'):
                    new_lines.append(f'2 CONT   -  {lines[i][7:]}')
                i += 1
        else:
            new_lines.append(line)
            i += 1

    with open(file_path, 'w') as file:
        file.writelines(new_lines)

replace_publ_with_note('/workspaces/gc2web/gen_site/Hoofman.ged')