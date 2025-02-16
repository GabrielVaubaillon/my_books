from pathlib import Path

import library as lib

from html_tables import works_table, books_table, authors_table


def create_collections(library: lib.Library) -> dict[str, set[str]]:
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
            file_content = works_table(library=library, works_ids=ids)
        elif name.endswith("_b"):
            file_content = books_table(library=library, books_ids=ids)
        elif name == "all_a":
            file_content = authors_table(library=library, authors_ids=ids)
        elif name == "read_a":
            file_content = authors_table(library=library, authors_ids=ids, sorting="read")
        elif name == "owned_b_a":
            file_content = authors_table(library=library, authors_ids=ids, sorting="owned_b")
        elif name == "owned_w_a":
            file_content = authors_table(library=library, authors_ids=ids, sorting="owned_w")
        else:
            # TODO: better handling (but dev side so not high priority)
            print("ERROR, collection not recognized:", name)
            file_content = ""

        if file_content:
            output_file = output_dir / (name + ".md")
            with open(output_file, mode="w", encoding="utf-8") as file:
                file.write(file_content)
