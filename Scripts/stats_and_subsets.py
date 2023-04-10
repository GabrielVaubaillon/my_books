import data_management as dm
from check_file import check_file


def prct(n, total):
    return f"{round((n*100)/total, 2)}%"


def main(filename):
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
        'liste_ebook': [],  # Nom liste_ebbok pour conserver le lien envoyé à la famille
        'antony': [],
        'avignon': [],
        'cork': [],
    }
    s_total = 0
    s_read = 0
    s_read_french = 0
    s_read_english = 0
    s_owned = 0
    s_owned_read = 0
    s_lent = 0
    s_french = 0
    s_english = 0
    s_authors = 0
    authors = []

    with open(filename, "r") as f:
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
        else:
            d['pas_lus'].append(book)

        if book.owned == "Possédé":
            s_owned += 1
            d['possedes'].append(book)
            if book.read == "Lu":
                s_owned_read += 1
            if book.language.startswith("Français"):
                d['possedes_francais'].append(book)
            elif book.language.startswith("English"):
                d['possedes_english'].append(book)

        if book.situation.startswith("Prêté"):
            s_lent += 1

        if book.language.startswith("Français"):
            s_french += 1
        elif book.language.startswith("English"):
            s_english += 1

        if book.author not in authors:
            s_authors += 1
            authors.append(book.author)

        if book.situation == "Ebook":
            locations['liste_ebook'].append(book)
        elif book.situation.startswith("Cork"):
            locations['cork'].append(book)
        elif book.situation.startswith("Antony"):
            locations['antony'].append(book)
        elif book.situation.startswith("Avignon"):
            locations['avignon'].append(book)

    stats = (f"-----------------------------------\n    Stats, sur tout mes livres\n-----------------------------------\n\n"
             f"Total livres: {s_total}\n"
             f"     - {s_read} ({prct(s_read, s_total)}) livres lus\n"
             f"         - {s_read_french} ({prct(s_read_french, s_read)}) lus en français\n"
             f"         - {s_read_english} ({prct(s_read_english, s_read)}) lus en anglais\n"
             f"     - {s_total - s_read} ({prct(s_total - s_read, s_total)}) non lus\n"
             f"     - {s_owned} ({prct(s_owned, s_total)}) livres possédé,\n"
             f"         - dont {s_owned_read} ({prct(s_owned_read, s_owned)}) lus\n"
             f"     - {s_total - s_owned} ({prct(s_total - s_owned, s_total)}) lus, mais pas à moi\n"
             f"     - {s_lent} livres prêté(s)\n"
             f"     - {s_french} ({prct(s_french, s_total)}) en Français\n"
             f"     - {s_english} ({prct(s_english, s_total)}) en Anglais\n"
             f"     - {s_authors} auteurs différents\n"
             )

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

        l_stats = (f"\n{loc_name}\n{'-'*len(loc_name)}\n"
                   f"  {l_total} livres, {prct(l_total,s_owned)} de la collection\n"
                   f"   - {l_read} ({prct(l_read, l_total)}) livres lus\n"
                   f"   - {l_french} ({prct(l_french, l_total)}) livres en français\n"
                   f"   - {l_english} ({prct(l_english, l_total)}) livres en anglais\n"
                   f"\n"
                   )
        stat_loc[k] = l_stats
        stats += l_stats

    with open("../stats.txt", "w") as f:
        f.write(stats)
        f.write("\n")

    for k, l in d.items():
        with open(path+k+".md", "w") as f:
            f.write(f"{k} sous liste\nComprend {len(l)} ({prct(len(l), s_total)}) livres parmis les {s_total} au total\n")
            f.write(dm.HEADER)
            for book in l:
                f.write(book.to_str())
                f.write("\n")
            f.write("\n")

    for k, l in locations.items():
        with open(path+k+".md", "w") as f:
            f.write(f"{k} sous liste\nComprend {len(l)} ({prct(len(l), s_total)}) livres parmis les {s_total} au total\n")
            f.write(stat_loc[k])
            f.write(dm.HEADER)
            for book in l:
                f.write(book.to_str())
                f.write("\n")
            f.write("\n")


if __name__ == "__main__":
    file = "../possedes_ou_lus.md"
    path = "../Sous_listes/"
    res = check_file(file)
    if res == 0:
        main(file)
        print("Done")
