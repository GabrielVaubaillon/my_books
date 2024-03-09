#!/bin/python
import os
import logging as log
import strictyaml as yaml

def check_valid(lib):
    # TODO: check all references are to existing keys (languages)
    # TODO: check no duplicate titles (in works)
    # TODO: check no duplicate authors
    # TODO: check valid isbn
    # TODO: check no book without work, no author without work
    # TODO: check no work not read AND without books 
    # TODO: check at least fr or english as title
    # TODO: check all languages have french and english names
    error_list = []
    return error_list

def percent(subset, original_set):
    return f"{len(subset)} ({round(len(subset)/len(original_set)*100, 2)}%)"

def sorted_authors_list(authors_id, lib, w_owned, w_read, key="name"):
    ids = list(authors_id)
    def sort_name(a_id, lib):
        name = lib["authors"][a_id]["sorting_name"].lower()
        fullname = lib["authors"][a_id]["name"].lower()
        return (name, fullname)
    def sort_owned(a_id, lib, w_owned):
        name = lib["authors"][a_id]["sorting_name"].lower()
        fullname = lib["authors"][a_id]["name"].lower()
        return (len(set(lib['authors'][a_id]['works']) & w_owned), name, fullname)
    def sort_read(a_id, lib, w_read):
        name = lib["authors"][a_id]["sorting_name"].lower()
        fullname = lib["authors"][a_id]["name"].lower()
        return (len(set(lib['authors'][a_id]['works']) & w_read), name, fullname)
    if key == "name":
        ids.sort(key=lambda x: sort_name(x, lib))
    elif key == "owned":
        ids.sort(key=lambda x: sort_owned(x, lib, w_owned))
        ids.reverse()
    elif key == "read":
        ids.sort(key=lambda x: sort_read(x, lib, w_read))
        ids.reverse()
    return ids

def sorted_book_list(book_ids, lib):
    ids = list(book_ids)

    def sorting_key(b_id, lib):
        authors = lib["works"][lib["books"][b_id]["works"][0]]["authors"]
        if len(authors) == 0:
            author = "zz"
            fullname = "zzz"
        else:
            author = lib["authors"][authors[0]]["sorting_name"].lower()
            fullname = lib["authors"][authors[0]]["name"].lower()
        title = lib["books"][b_id]["title"]
        situation = lib["books"][b_id]["situation"]
        serie = lib["books"][b_id].get("serie", "")
        serie_place = lib["books"][b_id].get("serie_position", "")
        return (author, fullname, serie, serie_place, title, situation)

    ids.sort(key=lambda x: sorting_key(x, lib))
    return ids

def sorted_works_list(work_ids, lib):
    ids = list(work_ids)

    def sorting_key(w_id, lib):
        authors = lib["works"][w_id]["authors"]
        if len(authors) == 0:
            author = "zz"
            fullname = "zzz"
        else:
            author = lib["authors"][authors[0]]["sorting_name"].lower()
            fullname = lib["authors"][authors[0]]["name"].lower()
        if "fr" in lib["works"][w_id]["titles"]:
            title = lib["works"][w_id]["titles"]["fr"]
        else:
            title = lib["works"][w_id]["titles"]["en"]
        serie = lib["works"][w_id].get("serie", "")
        serie_place = lib["works"][w_id].get("serie_position", "")
        return (author, fullname, serie, serie_place, title)

    ids.sort(key=lambda x: sorting_key(x, lib))
    return ids

def works_from_books(b_ids, lib):
    w_ids = set()
    for b_id in b_ids:
        for w in lib["books"][b_id]["works"]:
            w_ids.add(w)
    return w_ids

def books_from_works(w_ids, lib):
    b_ids = set()
    for w_id in w_ids:
        for b in lib["works"][w_id]["books"]:
            b_ids.add(b)
    return b_ids
    
def html_table_books(b_ids, lib):
    if not b_ids:
        return [""]

    table = [
        "<table>",
        "\t<thead>",
        "\t\t<tr>",
        "\t\t\t<th colspan=2>Titre</th>",
        "\t\t\t<th>Auteur·rice</th>",
        "\t\t\t<th>Langue</th>",
        "\t\t\t<th>Lu</th>",
        "\t\t\t<th>Situation</th>",
        #"\t\t\t<th>Notes</th>", # TODO: add notes
        "\t\t</tr>",
        "\t</thead>",
        "\t<tbody>",
    ]

    sorted_b_ids = sorted_book_list(b_ids, lib)

    for b_id in sorted_b_ids:
        # title (title work) author language read situation notes
        book = lib["books"][b_id]
        nb_works = len(book["works"])
        table.append("\t\t<tr>")
        if nb_works == 1:
            work = lib["works"][book["works"][0]]
            # TODO: add english/French name when possible
            if book["title"] == work["titles"][book["language"]]:
                table.append(f"\t\t\t<td colspan=2>{book['title']}</td>")
            else:
                table.append(f"\t\t\t<td>{book['title']}</td>")
                table.append(f"\t\t\t<td>{work['titles'][book['language']]}</td>")
            authors = " / ".join([lib["authors"][a]['name'] for a in work["authors"]])
            if work["read"]:
                read = "Lu"
            else:
                read = "Pas Lu"
            table += [
                f"\t\t\t<td>{authors}</td>",
                f"\t\t\t<td>{book['language']}</td>",
                f"\t\t\t<td>{read}</td>",
                f"\t\t\t<td>{book['situation']}</td>",
            ]
            table.append("\t\t</tr>")
        else:
            # one_author 
            one_author = True
            authors = []
            for w_id in book["works"]:
                if not authors:
                    authors = lib["works"][w_id]["authors"]
                if lib["works"][w_id]["authors"] != authors:
                    on_author = False
                    break
            # all read or all not_read
            one_read_status = True
            read = None
            for w_id in book["works"]:
                if read is None:
                    read = lib["works"][w_id]["read"]
                if lib["works"][w_id]["read"] != read:
                    one_read_status = False
                    break
            first_work = lib["works"][book["works"][0]]
            table += [
                f"\t\t\t<td rowspan={nb_works}>{book['title']}</td>",
                f"\t\t\t<td>{first_work['titles'][book['language']]}</td>",
            ]
            authors = " / ".join([lib["authors"][a]['name'] for a in first_work["authors"]])
            if one_author:
                table.append(f"\t\t\t<td rowspan={nb_works}>{authors}</td>")
            else:
                table.append(f"\t\t\t<td>{authors}</td>")
            table.append(f"\t\t\t<td rowspan={nb_works}>{book['language']}</td>")
            if first_work['read']:
                read = "Lu"
            else:
                read = "Pas Lu"
            if one_read_status:
                table.append(f"\t\t\t<td rowspan={nb_works}>{read}</td>")
            else:
                table.append(f"\t\t\t<td>{read}</td>")
            table.append(f"\t\t\t<td rowspan={nb_works}>{book['situation']}</td>")
            table.append("\t\t</tr>")

            for w_id in book["works"][1:]:
                work = lib["works"][w_id]
                table += [
                    "\t\t<tr>",
                    f"\t\t\t<td>{work['titles'][book['language']]}</td>",
                ]
                if not one_author:
                    authors = " / ".join([lib["authors"][a]['name'] for a in work["authors"]])
                    table.append(f"\t\t\t<td>{authors}</td>")
                if not one_read_status:
                    if work["read"]:
                        read = "Lu"
                    else:
                        read = "Pas Lu"
                    table.append(f"\t\t\t<td>{read}</td>")
                table.append("\t\t</tr>")
    table += [
        "\t</tbody>",
        "</table>",
    ]
    return table

def html_table_works(w_ids, lib):
    if not w_ids:
        return [""]

    table = [
        "<table>",
        "\t<thead>",
        "\t\t<tr>",
        "\t\t\t<th>Titre</th>",
        "\t\t\t<th>Auteur·rice</th>",
        #"\t\t\t<th>Langue</th>",
        "\t\t\t<th>Lu</th>",
        "\t\t\t<th>Possédé</th>",
        #"\t\t\t<th>Notes</th>", # TODO: add notes
        "\t\t</tr>",
        "\t</thead>",
        "\t<tbody>",
    ]

    sorted_w_ids = sorted_works_list(w_ids, lib)

    for w_id in sorted_w_ids:
        work = lib["works"][w_id]
        if "fr" in work["titles"]:
            title = work["titles"]["fr"]
        else:
            title = work["titles"]["en"]
        authors = " / ".join([lib["authors"][a]['name'] for a in work["authors"]])
        if work["books"]:
            owned = "Possédé"
        else:
            owned = "Non Possédé"
        if work["read"]:
            read = "Lu"
        else:
            read = "Pas Lu"
        table += [
            "\t\t<tr>",
            f"\t\t\t<td>{title}</td>",
            f"\t\t\t<td>{authors}</td>",
            f"\t\t\t<td>{read}</td>",
            f"\t\t\t<td>{owned}</td>",
            "\t\t</tr>",
        ]
    table += [
        "\t</tbody>",
        "</table>",
    ]
    return table

def html_table_authors(a_ids, lib, w_owned, w_read, key="name"):
    # key in ["name", "owned", "read"]
    table = [
        "<table>",
        "\t<thead>",
        "\t\t<tr>",
        "\t\t\t<th>Auteur·rice</th>",
        "\t\t\t<th>Nombre oeuvres lues</th>",
        "\t\t\t<th>Nombre oeuvres possédées</th>",
        "\t\t</tr>",
        "\t</thead>",
        "\t<tbody>",
    ]

    sorted_a_ids = sorted_authors_list(a_ids, lib, w_owned, w_read, key=key)
    
    for a_id in sorted_a_ids:
        table += [
            "\t\t<tr>",
            f"\t\t\t<td>{lib['authors'][a_id]['name']}</td>",
            f"\t\t\t<td>{len(set(lib['authors'][a_id]['works']) & w_read)}</td>",
            f"\t\t\t<td>{len(set(lib['authors'][a_id]['works']) & w_owned)}</td>",
            "\t\t</tr>",
        ]
    table += [
        "\t</tbody>",
        "</table>",
    ]
    return table

def main():
    log.debug("Entering main()")
    # TODO: out of the code, should be passed as argument
    work_dir = "."
    input_filename = "../books.yaml"


    log.debug(f"Reading {input_filename}")
    with open(input_filename, mode="r", encoding="utf-8") as input_file:
        lines = input_file.readlines()
    yaml_str = "".join(lines)

    schema = yaml.Map({
        "languages": yaml.MapPattern(yaml.Str(), yaml.MapPattern(yaml.Str(), yaml.Str())),
        "works": yaml.MapPattern(yaml.Str(), yaml.Map({
            "titles": yaml.MapPattern(yaml.Str(), yaml.Str()),
            "language": yaml.Str(),
            "read": yaml.Bool(),
            "books": yaml.Str(),
            "authors": yaml.Str(),
            yaml.Optional("notes"): yaml.Str()
            })),
        "books": yaml.MapPattern(yaml.Str(), yaml.Map({
            "title": yaml.Str(),
            "language": yaml.Str(),
            "isbn": yaml.Str(),
            "situation": yaml.Str(),
            yaml.Optional("notes"): yaml.Str()
            })),
        "authors": yaml.MapPattern(yaml.Str(), yaml.Map({
            "name": yaml.Str(),
            yaml.Optional("sorting_name"): yaml.Str(),
            yaml.Optional("notes"): yaml.Str()
            })),
        "series": yaml.MapPattern(yaml.Str(), yaml.Map({
            "name": yaml.MapPattern(yaml.Str(), yaml.Str()),
            yaml.Optional("works"): yaml.MapPattern(yaml.Str(), yaml.Str()),
            yaml.Optional("abbreviation"): yaml.Str(),
            yaml.Optional("subseries"): yaml.MapPattern(yaml.Str(), yaml.Str()),
            yaml.Optional("notes"): yaml.Str()
            }))
     })

    log.info("- Loading yaml")
    yaml_library = yaml.load(yaml_str, schema)
    log.debug("- Checking structure")
    error_list = check_valid(yaml_library)
    if error_list:
        return

    lib = yaml_library.data

    # Make two way link authors<->works<->books (from authors<-works->books)
    log.info("- Loading library")
    log.debug("Casting semicolon-separated strings to lists")
    for w in lib["works"].values():
        for key in ("books", "authors"):
            if w[key]:
                w[key] = w[key].split(";")
            else:
                w[key] = []

    log.debug("Linking works to authors and works to books")
    for w_id, w in lib["works"].items():
        for key in ("books", "authors"):
            for i in w[key]:
                if "works" not in lib[key][i]:
                    lib[key][i]["works"] = [w_id]
                else:
                    lib[key][i]["works"].append(w_id)

    log.debug("Creating sorting names for authors")
    for a_id, a in lib["authors"].items():
        if "sorting_name" not in a:
            a["sorting_name"] = a["name"].split(" ")[-1]
        a["sorting_name"] = a["sorting_name"].lower()

    log.debug("Adding Serie info in works and books")
    for s_id, s in lib["series"].items():
        if "works" in s:
            for place, w_id in s["works"].items():
                lib["works"][w_id]["serie"] = s_id
                lib["works"][w_id]["serie_position"] = place
                for b_id in lib["works"][w_id]["books"]:
                    if "serie" not in lib["books"][b_id] or lib["books"][b_id]["serie"] > s_id:
                        lib["books"][b_id]["serie"] = s_id
                    if "serie_position" not in lib["books"][b_id] or lib["books"][b_id]["serie_position"] > place:
                        lib["books"][b_id]["serie_position"] = place

    log.info("- Library loaded and ready to use")

    b_total = {b_id for b_id in lib["books"]}
    w_total = {w_id for w_id in lib["works"]}
    a_total = {a_id for a_id in lib["authors"]}

    log.info("- Extracting subsets")

    b_owned = {b_id for b_id in b_total if lib["books"][b_id]["situation"]}
    w_owned = works_from_books(b_owned, lib)

    w_read = {w_id for w_id in w_total if lib["works"][w_id]["read"]}
    b_read = books_from_works(w_read, lib)
    
    w_read_not_owned = w_read - w_owned

    w_owned_not_read = w_owned - w_read # Must do in this order for partially read books
    b_owned_not_read = books_from_works(w_owned_not_read, lib)

    w_owned_read = w_owned & w_read
    b_owned_read = books_from_works(w_owned_read, lib)

    b_owned_french = {b_id for b_id in b_owned if lib["books"][b_id]["language"] == "fr"}
    w_owned_french = works_from_books(b_owned_french, lib)

    b_owned_english = {b_id for b_id in b_owned if lib["books"][b_id]["language"] == "en"}
    w_owned_english = works_from_books(b_owned_english, lib)

    a_owned = set()
    a_read = set()
    for a_id in a_total:
        for w_id in lib["authors"][a_id]["works"]:
            if w_id in w_owned:
                a_owned.add(a_id)
            if w_id in w_read:
                a_read.add(a_id)

    b_by_situation = {}
    situations = set()
    for b_id in b_owned:
        situation = lib["books"][b_id]["situation"].split("/")[0]
        if situation.startswith("Prêté"):
            continue
        if situation in b_by_situation:
            b_by_situation[situation].add(b_id)
        else:
            b_by_situation[situation] = {b_id}
        situations.add(situation)
    w_by_situation = {situation: works_from_books(b_by_situation[situation],lib) for situation in situations}
    log.debug(f"Found {len(situations)} places: {situations}")
    # log.debug(f"w_by_situation: {w_by_situation}")

    situations_subsets = {}
    for s, b_s in b_by_situation.items():
        w_s = w_by_situation[s]
        situations_subsets[s] = {
            "owned_read": b_s & books_from_works(w_s & w_read, lib),
            "w_owned_read": w_s & w_read,
            "owned_not_read": b_s & books_from_works(w_s - w_read, lib),
            "w_owned_not_read": w_s - w_read,
            "owned_french": b_s & b_owned_french,
            "owned_english": b_s & b_owned_english,
        }
        
    log.debug("Creating html tables")

    table_all = html_table_works(w_total, lib)
    table_all_authors = html_table_authors(a_total, lib, w_owned, w_read, key="name")
    table_owned = html_table_books(b_owned, lib)
    table_read = html_table_works(w_read, lib)
    table_read_not_owned = html_table_works(w_read_not_owned, lib)
    table_owned_not_read = html_table_books(b_owned_not_read, lib)
    table_owned_read = html_table_books(b_owned_read, lib)
    table_owned_french = html_table_books(b_owned_french, lib)
    table_owned_english = html_table_books(b_owned_english, lib)
    table_authors_owned = html_table_authors(a_owned, lib, w_owned, w_read, key="owned")
    table_authors_read = html_table_authors(a_read, lib, w_owned, w_read, key="read")

    tables_by_situation = {}
    for situation in situations:
        tables_by_situation[situation] = {}
        tables_by_situation[situation]["owned"] = html_table_books(b_by_situation[situation],lib)
        for name, subset in situations_subsets[situation].items():
            if name.startswith("w_"):
                continue
            tables_by_situation[situation][name] = html_table_books(subset, lib)

    # TODO: add header in files
    files_to_write = {
        "all": table_all,
        "owned": table_owned,
        "read": table_read,
        "read_not_owned": table_read_not_owned,
        "owned_not_read": table_owned_not_read,
        "owned_read": table_owned_read,
        "owned_french": table_owned_french,
        "owned_english": table_owned_english,
        "authors": table_all_authors,
        "authors_owned": table_authors_owned,
        "authors_read": table_authors_read,
    }
    for situation, subsets in tables_by_situation.items():
        for subset_name, table in subsets.items():
            name = situation.lower() + "_" + subset_name
            files_to_write[name] = table

    log.info("- Writing markdown files")

    for filename, table in files_to_write.items():
        if len(table) < 2:
            log.debug(f"{filename} is empty, no file")
            continue
        log.debug(f"Writing {filename}")
        # TODO: proper PATH management
        with open(f"../Lists/{filename}.md", mode="w", encoding="utf-8") as f:
            f.write("\n".join(table))

    readme = [
        "# Mes livres - lus et possédés",
        # "[Click here for English](README_EN.md), # TODO
        "## Liens rapides",
        "[Tous](Lists/all.md)",
        "",
        "[Livres lus](Lists/read.md)",
        "",
        "[Livres possédés](Lists/owned.md)",
        "",
        "[Livres numériques](Lists/ebook_owned.md)",
        "## Statistiques",
        # TODO: faq livres vs oeuvres
        f"### Collection [({len(b_owned)} livres / {len(w_owned)} oeuvres)](Lists/owned.md)",
        f"- [{percent(w_owned_read, w_owned)} oeuvres lues](Lists/owned_read.md)",
        f"- [{percent(w_owned_not_read, w_owned)} oeuvres à lire](Lists/owned_not_read.md)",
        f"- [{percent(b_owned_french, b_owned)} livres en français](Lists/owned_french.md)",
        f"- [{percent(b_owned_english, b_owned)} livres en anglais](Lists/owned_english.md)",
        f"- [{len(a_owned)} auteurs differents](Lists/authors_owned.md)"
        # TODO: lended/borrowed books
    ]
    list_situations = list(situations)
    list_situations.sort()
    for situation in list_situations:
        s_prefix = situation.lower()
        w_s_owned = w_by_situation[situation]
        b_s_owned = b_by_situation[situation]
        readme += [
            f"- [{situation}: {percent(b_s_owned, b_owned)} livres, {percent(w_s_owned, w_owned)} oeuvres](Lists/{s_prefix}_owned.md)",
            f"   - [{percent(situations_subsets[situation]['w_owned_read'], w_s_owned)} oeuvres lues](Lists/{s_prefix}_owned_read.md)",
            f"   - [{percent(situations_subsets[situation]['w_owned_not_read'], w_s_owned)} oeuvres à lire](Lists/{s_prefix}_owned_not_read.md)",
            f"   - [{percent(situations_subsets[situation]['owned_french'], b_s_owned)} livres en français](Lists/{s_prefix}_owned_french.md)",
            f"   - [{percent(situations_subsets[situation]['owned_english'], b_s_owned)} livres en anglais](Lists/{s_prefix}_owned_english.md)",
        ]
    readme += [
        f"### Lus [({len(w_read)} oeuvres)](Lists/read.md)",
        f"- [{percent(w_owned_read, w_read)} oeuvres lues parmis ma collection actuelle](Lists/owned_read.md)",
        f"- [{percent(w_read_not_owned, w_read)} oeuvres lues hors ma collection actuelle](Lists/read_not_owned.md)",
        f"- [{len(a_read)} auteurs differents](Lists/authors_read.md)",
        f"### Autres",
        f"- [Toutes les oeuvres](Lists/all.md)",
        #f"- x séries",
        #f"- langues originales des oeuvres:",
    ]
    with open("../README.md", mode="w", encoding="utf-8") as f:
        f.write("\n".join(readme))

if __name__ == "__main__":
    log.basicConfig(format=' %(levelname)-8s (%(asctime)s) %(message)s', level=log.DEBUG)
    main()

