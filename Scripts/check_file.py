#!/usr/bin/env python3
import re
import data_management as dm


def check_file(filename, override_short=False):
    return_value = 0
    print(f"Open {filename}")
    with open(filename, "r") as f:
        lines = f.readlines()
    print("Checking file not empty")
    if len(lines) < 4 and not override_short:
        print(f"FILE ({filename}) TOO SHORT, PROBLEM SOMEWHERE PLEASE CHECK")
        return 1
    lines = [line[:-1] for line in lines]  # Get rid of \n
    print("Checking Empty line at the end of the file")
    if len(lines[-1]) > 0:
        print("No empty line at the end of the file")
        return 2
    lines = lines[:-1]

    columns_pattern = re.compile(r"""^\|( [^|]*\|){8}$""")

    print("Checking  all lines have right number of columns")
    for i, line in enumerate(lines):
        if not (re.match(columns_pattern, line)):
            print(f"{i+1}: not right number of columns or wrong space pattern {line}")
            return_value = 3
    if return_value != 0:
        return return_value

    print("Checking books can be extracted from file")
    try:
        with open(filename, "r") as f:
            library = dm.list_from_md_file(f)
    except Exception as e:
        print(f"{e}\n\nCannot charge the library, verify {filename} format")
        return 4

    print("Checking values seems correct in columns for each book")
    for i,book in enumerate(library):
        if book.owned not in ["Possédé", "Non"]:
            print(f"{i+3}: {book.title}, {book.author}: Invalid value Column Possédé: '{book.owned}'")
            return_value = 5
        if book.read not in ["Lu", "Pas Lu", ""]:
            print(f"{i+3}: {book.title}, {book.author}: Invalid value Column Lu: '{book.read}'")
            return_value = 5
        if book.language not in ["English", "English (tr.)", "Français", "Français (tr.)", "English/Français"]:
            print(f"{i+3}: {book.title}, {book.author}: Invalid value Column Langue: '{book.language}'")
            return_value = 5
        if (book.situation not in dm.WRITTEN_LOCATIONS) and not book.situation.startswith("Prêté"):
            print(f"WARNING: {i+3}, {book.title}, {book.author}: Situation ('{book.situation}') not known, check spelling or update checks")

    if return_value != 0:
        return return_value

    print("File checked : no error found")
    return 0


if __name__ == "__main__":
    import os
    script_dir = os.path.abspath(os.path.dirname(__file__))
    file = os.path.join(script_dir, "../possedes_ou_lus.md")
    check_file(file)
