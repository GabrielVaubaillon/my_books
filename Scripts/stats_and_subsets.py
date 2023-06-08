#!/usr/bin/env python3
import os
import shutil

import data_management as dm
from check_file import check_file


def prct(n, total):
    return f"{round((n*100)/total, 2)}%"


def main(data_file_path, list_directory, readme_path):
    d = {
        'possedes': [],
        'lus': [],
        'pas_lus': [],
        'possedes_francais': [],
        'lus_francais': [],
        'possedes_english': [],
        'lus_english': [],
    }
    locations = {}
    for k in dm.LOCATIONS.keys():
        locations[k] = []
    s_total = 0
    s_read = 0
    s_read_french = 0
    s_read_english = 0
    s_owned_french = 0
    s_owned_english = 0
    s_owned = 0
    s_owned_read = 0
    s_lent = 0
    s_french = 0
    s_english = 0
    authors_tot = {}
    authors_owned = []
    authors_read = []

    print(f"Opening file {data_file_path}")
    with open(data_file_path, "r") as f:
        library = dm.list_from_md_file(f)

    print("Iterating over all books, counting for stats and filling sublists")
    for book in library:
        s_total += 1
        if book.read == "Lu":
            d['lus'].append(book)
            s_read += 1
            if book.language.startswith("Français"):
                s_read_french += 1
                d['lus_francais'].append(book)
            elif book.language.startswith("English"):
                s_read_english += 1
                d['lus_english'].append(book)
            if book.author not in authors_read:
                authors_read.append(book.author)
        else:
            d['pas_lus'].append(book)

        if book.owned == "Possédé":
            s_owned += 1
            d['possedes'].append(book)
            if book.read == "Lu":
                s_owned_read += 1
            if book.language.startswith("Français"):
                d['possedes_francais'].append(book)
                s_owned_french += 1
            elif book.language.startswith("English"):
                d['possedes_english'].append(book)
                s_owned_english += 1
            if book.author not in authors_owned:
                authors_owned.append(book.author)

        if book.situation.startswith("Prêté"):
            s_lent += 1

        if book.language.startswith("Français"):
            s_french += 1
        elif book.language.startswith("English"):
            s_english += 1

        if book.author not in authors_tot.keys():
            authors_tot[book.author] = 1
        else:
            authors_tot[book.author] += 1

        for l in locations.keys():
            if book.situation.lower().startswith(l):
                locations[l].append(book)

    s_authors = len(authors_tot.keys())
    s_read_authors = len(authors_read)
    s_owned_authors = len(authors_owned)

    print("General stats done")
    stats = [(f"## Stats\n"
              f"\n### Ma collection\n\n"
              f"- {s_owned} livres possédés ({prct(s_owned, s_total)} du total)\n"
              f"- {s_owned_read} livres lus ({prct(s_owned_read, s_owned)})\n"
              f"- et {s_owned-s_owned_read} non lus ({prct(s_owned-s_owned_read, s_owned)})\n"
              f"- {s_owned_french} livres en français ({prct(s_owned_french, s_owned)})\n"
              f"- {s_owned_english} livres en anglais ({prct(s_owned_english, s_owned)})\n"
              f"- {s_owned_authors} auteurs différents\n"
              f"- {s_lent} livres prêté(s)\n"
              ), (
              f"\n### Mes Lus\n\n"
              f"- {s_read} livres lus ({prct(s_read, s_total)} du total)\n"
              f"- {s_read_french} ({prct(s_read_french, s_read)}) lus en français\n"
              f"- {s_read_english} ({prct(s_read_english, s_read)}) lus en anglais\n"
              f"- {s_read_authors} auteurs différents\n"
              f"\n### Total\n\n"
              f"- {s_total} livres\n"
              f"- {s_french} ({prct(s_french, s_total)}) en Français\n"
              f"- {s_english} ({prct(s_english, s_total)}) en Anglais\n"
              f"- {s_authors} auteurs différents\n"
              f"- {s_total - s_owned} ({prct(s_total - s_owned, s_total)}) hors collection, mais lus\n"
             )]

    print("Generating stats for specific locations:")
    stat_loc = {}
    for k, l in locations.items():
        print(f"  - {k.capitalize()}")
        l_total = 0
        l_read = 0
        l_french = 0
        l_english = 0

        for book in l:
            l_total += 1
            if book.read == "Lu":
                l_read += 1
            if book.language.startswith("Français"):
                l_french += 1
            elif book.language.startswith("English"):
                l_english += 1

        l_stats = (f"- {k.capitalize()}\n"
                   f"    - {l_total} livres ({prct(l_total,s_owned)} de la collection)\n"
                   f"    - {l_read} livres lus ({prct(l_read, l_total)})\n"
                   f"    - {l_french} livres en français ({prct(l_french, l_total)})\n"
                   f"    - {l_english} livres en anglais ({prct(l_english, l_total)})\n"
                   )
        stat_loc[k] = l_stats
        stats[0] += l_stats
    stats = stats[0] + stats[1]

    print(f"Saving start of README file ({readme_path})")
    full_string = ""
    with open(readme_path, "r") as f:
        str_ = f.readline()
        while str_ != "<!-- Everything after this line is auto-generated -->\n":
            full_string += str_
            str_ = f.readline()
        full_string += str_
    full_string += stats

    print("Writing README with all stats at the end")
    with open(readme_path, "w") as f:
        f.write(full_string)

    print(f"Cleaning Sous_listes/ directory ({list_directory})")
    for filename in os.listdir(list_directory):
        if filename != "README.md":
            os.remove(os.path.join(list_directory, filename))

    print("Writing sublists (not specific locations)")
    for k, l in d.items():
        with open(list_directory+k+".md", "w") as f:
            f.write(f"## {k} \n - {len(l)} parmi les {s_total} ({prct(len(l), s_total)})\n\n")
            f.write(dm.HEADER)
            for book in l:
                f.write(book.to_str())
                f.write("\n")
            f.write("\n")

    print("Writing location specific sublists")
    for k, l in locations.items():
        with open(list_directory+k+".md", "w") as f:
            f.write(stat_loc[k])
            f.write("\n")
            f.write(dm.HEADER)
            for book in l:
                f.write(book.to_str())
                f.write("\n")
            f.write("\n")
    # shared the link to liste_ebook, need to keep it alive:
    shutil.copy(list_directory+"ebook.md", list_directory+"liste_ebook.md")

    print("Writing list of authors")
    with open(list_directory+"auteurs.md", "w") as f:
        f.write(f"{s_authors} Auteurs différents\n\n| Auteur | nb livres lus ou possédés |\n| --- | --- |\n")
        list_ = list(authors_tot.items())
        list_.sort(reverse=True, key=lambda e: e[1])
        for (author, number) in list_:
            f.write(f"| {author} | {number} |\n")
    print("Stats and sublists Done")


if __name__ == "__main__":
    script_dir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.normpath(os.path.join(script_dir, "../possedes_ou_lus.md"))
    list_path = os.path.normpath(os.path.join(script_dir, "../Sous_listes/"))
    readme_path = os.path.normpath(os.path.join(script_dir, "../README.md"))
    if not os.path.isfile(file_path) or (not os.path.isdir(list_path)):
        exit(1)
    res = check_file(file_path)
    if res == 0:
        main(file_path, list_path, readme_path)
        print("Done")
