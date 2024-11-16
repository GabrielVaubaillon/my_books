#!/bin/python
import argparse
from pathlib import Path
import re

import library as lib


def _parse_cli_args():
    # TODO: add descriptions
    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("output_stat_file", type=Path)
    return parser.parse_args()


def percent(number: int, total: int):
    if number == 0:
        return "0"
    if number == total:
        return f"{number} (100%)"
    return f"{number} ({round(number/total*100, 2)}%)"


def create_collections(library: lib.Library) -> dict[str, set[str]]:
    # TODO: add original languages
    # TODO: change that. I'm not happy with this part
    collections = {
        "all_w": set(library.works.keys()),
        "all_b": set(library.books.keys()),
        "all_a": set(library.authors.keys()),
        "owned_w": {id for id, work in library.works.items() if work.owned},
        "owned_b": {id for id, book in library.books.items() if book.situation},
        # the owned_a can be sorted two ways
        "owned_w_a": {id for id, author in library.authors.items() if author.books_owned},
        "owned_b_a": {id for id, author in library.authors.items() if author.books_owned},
        "read_w": {id for id, work in library.works.items() if work.read},
        "read_a": {id for id, author in library.authors.items() if author.works_read},
        "read_b": {id for id, book in library.books.items() if book.partial_read},
        "read_owned_w": {id for id, work in library.works.items() if work.read and work.owned},
        "read_owned_b": {
            id for id, book in library.books.items() if book.partial_read and book.situation
        },
        "unread_owned_w": {
            id for id, work in library.works.items() if (not work.read) and work.owned
        },
        "unread_owned_b": {
            id for id, book in library.books.items() if (not book.fully_read) and book.situation
        },
        "read_not_owned_w": {
            id for id, work in library.works.items() if work.read and (not work.owned)
        },
    }
    # languages
    for language in library.owned_languages:
        collections[f"owned_{language}_b"] = set()
        collections[f"owned_{language}_w"] = set()
        for id, book in library.books.items():
            if book.language == language and book.situation:
                collections[f"owned_{language}_b"].add(id)
                for w_id in book.works:
                    collections[f"owned_{language}_w"].add(w_id)

    # situations
    for situation in library.situations:
        sit = situation.lower()
        collections[f"owned_{sit}_b"] = set()
        collections[f"owned_{sit}_w"] = set()
        collections[f"read_owned_{sit}_b"] = set()
        collections[f"read_owned_{sit}_w"] = set()
        collections[f"unread_owned_{sit}_b"] = set()
        collections[f"unread_owned_{sit}_w"] = set()
        for language in library.owned_languages:
            collections[f"owned_{language}_{sit}_b"] = set()
            collections[f"owned_{language}_{sit}_w"] = set()

        for id, book in library.books.items():
            if book.situation.startswith(situation):
                collections[f"owned_{sit}_b"].add(id)
                if book.partial_read:
                    collections[f"read_owned_{sit}_b"].add(id)
                if not book.fully_read:
                    collections[f"unread_owned_{sit}_b"].add(id)

                collections[f"owned_{book.language}_{sit}_b"].add(id)
                for w_id in book.works:
                    collections[f"owned_{book.language}_{sit}_w"].add(w_id)
                    collections[f"owned_{sit}_w"].add(w_id)
                    if book.partial_read:
                        collections[f"read_owned_{sit}_w"].add(w_id)
                    if not book.fully_read:
                        collections[f"unread_owned_{sit}_w"].add(w_id)
    return collections


def setup_output_dir(output_dir: Path):
    if output_dir.is_dir():
        for file in output_dir.glob("*.md"):
            file.unlink()
    else:
        output_dir.mkdir(parents=True, exist_ok=True)


def dump_collections(library: lib.Library, collections: dict[str, set[str]], output_dir: Path):
    setup_output_dir(output_dir)

    for name, ids in collections.items():
        file_content: str
        if name.endswith("_w"):
            file_content = library.works_html_table(works_ids=ids)
        elif name.endswith("_b"):
            file_content = library.books_html_table(books_ids=ids)
        elif name == "all_a":
            file_content = library.authors_html_table(authors_ids=ids)
        elif name == "read_a":
            file_content = library.authors_html_table(authors_ids=ids, sorting="read")
        elif name == "owned_b_a":
            file_content = library.authors_html_table(authors_ids=ids, sorting="owned_b")
        elif name == "owned_w_a":
            file_content = library.authors_html_table(authors_ids=ids, sorting="owned_w")
        else:
            # TODO: better handling (but dev side so not high priority)
            print("ERROR, collection not recognized:", name)
            file_content = ""

        if file_content:
            output_file = output_dir / (name + ".md")
            with open(output_file, mode="w", encoding="utf-8") as file:
                file.write(file_content)


def write_stat_file(
    collections: dict[str, set[str]],
    collections_files_dir: Path,
    output_file: Path,
    lang: dict[str, lib.Language],
    owned_languages: list[str],
    situations: list[str],
):
    assert collections_files_dir.is_dir()
    stats: dict[str, int] = {name: len(collection) for name, collection in collections.items()}
    # TODO: get relative path from stat file to collections
    root_dir: Path = output_file.parent
    collections_relative_path: Path = collections_files_dir.relative_to(root_dir)

    owned_w: int = stats["owned_w"]
    owned_b: int = stats["owned_b"]

    lines: list[str] = [
        "# Mes livres - Lus et possédés",
        "",
        (
            "- Toutes les oeuvres, lues et/ou possédées: "
            f"[{stats["all_w"]}]({collections_relative_path}/all_w.md)"
        ),
        f"- Tous les livres: [{stats["all_b"]}]({collections_relative_path}/all_b.md)",
        f"- Oeuvres lues: [{stats["read_w"]}]({collections_relative_path}/read_w.md)",
        (
            "- Livres à lire: "
            f"[{stats["unread_owned_b"]}]({collections_relative_path}/unread_owned_b.md)"
        ),
        (
            f"- Livres numériques: "
            f"[{stats["owned_ebook_b"]}]({collections_relative_path}/owned_ebook_b.md)"
        ),
        "",
        "## Ma bibliothèque:",
        "",
        f"- [{owned_b}]({collections_relative_path}/owned_b.md) livres,",
        f"- [{percent(owned_w, stats["all_w"])}]({collections_relative_path}/owned_w.md) oeuvres.",
        (
            f"- Oeuvres lues: "
            f"[{percent(stats["read_owned_w"], owned_w)}]"
            f"({collections_relative_path}/read_owned_w.md)"
            " (reparties en "
            f"[{percent(stats["read_owned_b"], owned_b)}]"
            f"({collections_relative_path}/read_owned_b.md) livres)."
        ),
        (
            "- Oeuvres non lues : "
            f"[{percent(stats["unread_owned_w"], owned_w)}]"
            f"({collections_relative_path}/unread_owned_w.md)"
            " (reparties en "
            f"[{percent(stats["unread_owned_b"], owned_b)}]"
            f"({collections_relative_path}/unread_owned_b.md) livres)."
        ),
    ]
    for language in owned_languages:
        lines.append(
            f"- Livres en {lang[language].names["fr"]}"
            " : "
            f"[{percent(stats[f'owned_{language}_b'], owned_b)}]"
            f"({collections_relative_path}/owned_{language}_b.md)"
            " (contenant "
            f"[{percent(stats[f"owned_{language}_w"], owned_w)}]"
            f"({collections_relative_path}/owned_{language}_w.md) oeuvres)."
        )
    lines.append(
        "- Auteur·rice·s présent·e·s dans la collection: "
        f"{percent(stats["owned_w_a"], stats["all_a"])}, triés par "
        f"[nombre d'oeuvres]({collections_relative_path}/owned_w_a.md)"
        " ou par "
        f"[nombre de livres]({collections_relative_path}/owned_b_a.md)"
        " possédés"
    )

    for situation in situations:
        sit: str = situation.lower()
        owned_s_b: int = stats[f"owned_{sit}_b"]
        owned_s_w: int = stats[f"owned_{sit}_w"]
        lines += [
            f"- {situation}:",
            (
                "    - "
                f"[{percent(stats[f"owned_{sit}_b"], owned_b)}]"
                f"({collections_relative_path}/owned_{sit}_b.md) livres,"
            ),
            (
                "    - "
                f"[{percent(stats[f"owned_{sit}_w"], owned_w)}]"
                f"({collections_relative_path}/owned_{sit}_w.md) oeuvres."
            ),
            (
                f"    - Oeuvres lues: "
                f"[{percent(stats[f"read_owned_{sit}_w"], owned_s_w)}]"
                f"({collections_relative_path}/read_owned_{sit}_w.md)"
                " (reparties en "
                f"[{percent(stats[f"read_owned_{sit}_b"], owned_s_b)}]"
                f"({collections_relative_path}/read_owned_{sit}_b.md) livres)."
            ),
            (
                "    - Oeuvres non lues : "
                f"[{percent(stats[f"unread_owned_{sit}_w"], owned_s_w)}]"
                f"({collections_relative_path}/unread_owned_{sit}_w.md)"
                " (reparties en "
                f"[{percent(stats[f"unread_owned_{sit}_b"], owned_s_b)}]"
                f"({collections_relative_path}/unread_owned_{sit}_b.md) livres)."
            ),
        ]
        for language in owned_languages:
            lines.append(
                f"    - Livres en {lang[language].names["fr"]}"
                " : "
                f"[{percent(stats[f'owned_{language}_{sit}_b'], owned_s_b)}]"
                f"({collections_relative_path}/owned_{language}_{sit}_b.md)"
                " (contenant "
                f"[{percent(stats[f"owned_{language}_{sit}_w"], owned_s_w)}]"
                f"({collections_relative_path}/owned_{language}_{sit}_w.md) oeuvres)."
            )


    lines += [
        "",
        "## Mes lectures",
        "",
        f"- [{stats["read_w"]}]({collections_relative_path}/read_w.md) oeuvres lues.",
        (
            "- Oeuvres lues et possédées: "
            f"[{percent(stats["read_owned_w"], stats["read_w"])}]"
            f"({collections_relative_path}/read_owned_w.md)"
            " (reparties en "
            f"[{stats["read_owned_b"]}]({collections_relative_path}/read_owned_b.md) livres)."
        ),
        (
            "- Oeuvres lues et non possédées: "
            f"[{percent(stats["read_not_owned_w"], stats["read_w"])}]"
            f"({collections_relative_path}/read_not_owned_w.md)"
        ),
        (
            "- Auteur·rice·s lu·e·s: "
            f"[{percent(stats["read_a"], stats["all_a"])}]({collections_relative_path}/read_a.md)"
        ),
    ]

    lines += [
        "",
        "## Autres",
        "",
        f"Toutes les oeuvres: [{stats["all_w"]}]({collections_relative_path}/all_w.md",
        f"Tous les auteur·rice·s: [{stats["all_a"]}]({collections_relative_path}/all_a.md",
    ]

    file_content: str = "\n".join(lines)
    # Remove links to inexitent files (when 0 elements in it)
    file_content = re.sub(r"\[0]\(.*?\.md\)", "0", file_content)

    root_dir.mkdir(parents=True, exist_ok=True)
    with open(output_file, mode="w", encoding="utf-8") as file:
        file.write(file_content)


def main(input_file: Path, output_dir: Path, output_stats_file: Path) -> None:

    with open(input_file, mode="r", encoding="utf-8") as file:
        library_yaml = file.read()

    library = lib.load(library_yaml)

    collections = create_collections(library)

    for name, collection in collections.items():
        print(f"{name}: {len(collection)}")

    # Write files
    dump_collections(library, collections, output_dir)

    # Write Readme with library stats and links
    write_stat_file(
        collections=collections,
        collections_files_dir=output_dir,
        output_file=output_stats_file,
        lang=library.languages,
        owned_languages=library.owned_languages,
        situations=library.situations,
    )


if __name__ == "__main__":
    cli_args = _parse_cli_args()
    main(
        input_file=cli_args.input_filename,
        output_dir=cli_args.output_dir,
        output_stats_file=cli_args.output_stat_file,
    )
