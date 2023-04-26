#!/usr/bin/env python3
import os

import data_management as dm
from check_file import check_file


def prct(n, total):
    return f"{round((n*100)/total, 2)}%"


def main(data_file_path, list_directory):
    d = {
        'possedes': [],
        'lus': [],
        'pas_lus': [],
        'possedes_francais': [],
        'lus_francais': [],
        'possedes_english': [],
        'lus_english': [],
    }
    locations = {
        'liste_ebook': [],  # Nom liste_ebook pour conserver le lien envoyé à la famille
        'antony': [],
        'avignon': [],
        'cork': [],
    }
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

    with open(data_file_path, "r") as f:
        library = dm.list_from_md_file(f)

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

        if book.situation == "Ebook":
            locations['liste_ebook'].append(book)
        elif book.situation.startswith("Cork"):
            locations['cork'].append(book)
        elif book.situation.startswith("Antony"):
            locations['antony'].append(book)
        elif book.situation.startswith("Avignon"):
            locations['avignon'].append(book)

    s_authors = len(authors_tot.keys())
    s_read_authors = len(authors_read)
    s_owned_authors = len(authors_owned)

    stats = [(f"## Stats\n"
              f"\n### Ma collection\n\n"
              f"- {s_owned} livres possédés ({prct(s_owned, s_total)} du total)\n"
              f"- {s_owned_read} livres lus ({prct(s_owned_read, s_owned)})\n"
              f"- soit {s_owned-s_owned_read} non lus ({prct(s_owned-s_owned_read, s_owned)})\n"
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

    stat_loc = {}
    for k, l in locations.items():
        if k == "liste_ebook":
            loc_name = "Ebook"
        else:
            loc_name = k.capitalize()
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

        l_stats = (f"- {loc_name}\n"
                   f"    - {l_total} livres ({prct(l_total,s_owned)} de la collection)\n"
                   f"    - {l_read} livres lus ({prct(l_read, l_total)})\n"
                   f"    - {l_french} livres en français ({prct(l_french, l_total)})\n"
                   f"    - {l_english} livres en anglais ({prct(l_english, l_total)})\n"
                   )
        stat_loc[k] = l_stats
        stats[0] += l_stats
    stats = stats[0] + stats[1]

    full_string = ""
    with open("../README.md", "r") as f:
        str_ = f.readline()
        while str_ != "<!-- Everything after this line is auto-generated -->\n":
            full_string += str_
            str_ = f.readline()
        full_string += str_
    full_string += stats

    with open("../README.md", "w") as f:
        f.write(full_string)

    for filename in os.listdir(list_directory):
        if filename != "README.md":
            os.remove(os.path.join(list_directory, filename))

    for k, l in d.items():
        with open(list_directory+k+".md", "w") as f:
            f.write(f"## {k} \n - {len(l)} parmi les {s_total} ({prct(len(l), s_total)})\n\n")
            f.write(dm.HEADER)
            for book in l:
                f.write(book.to_str())
                f.write("\n")
            f.write("\n")

    for k, l in locations.items():
        with open(list_directory+k+".md", "w") as f:
            f.write(stat_loc[k])
            f.write("\n")
            f.write(dm.HEADER)
            for book in l:
                f.write(book.to_str())
                f.write("\n")
            f.write("\n")

    with open(list_directory+"auteurs.md", "w") as f:
        f.write(f"{s_authors} Auteurs différents\n\n| Auteur | nb livres lus ou possédés |\n| --- | --- |\n")
        for author, number in authors_tot.items():
            f.write(f"| {author} | {number} |\n")


if __name__ == "__main__":
    script_dir = os.path.abspath(os.path.dirname(__file__))
    file_path = os.path.join(script_dir, "../possedes_ou_lus.md")
    list_path = os.path.join(script_dir, "../Sous_listes/")
    if not os.path.isfile(file_path) or (not os.path.isdir(list_path)):
        exit(1)
    res = check_file(file_path)
    if res == 0:
        main(file_path, list_path)
        print("Done")
