import textwrap

from library import *


def books_table(library: Library, books_ids: set[str]) -> str:
    header: list[str] = [
        "<table>",
        "  <thead>",
        "    <tr>",
        "      <th colspan=2>Titre</th>",
        "      <th>Auteur·rice</th>",
        "      <th>Langue</th>",
        "      <th>Lu</th>",
        "      <th>Situation</th>",
        "    </tr>",
        "  </thead>",
        "  <tbody>",
        "",
    ]
    sorted_books_ids: list[str] = library.sort_books_ids(books_ids)
    body: list[str] = [book_row(library, book_id) for book_id in sorted_books_ids]
    footer: list[str] = [
        "",
        "  </tbody>",
        "</table>",
    ]
    str_ = "\n".join(header) + textwrap.indent("\n".join(body), "    ") + "\n".join(footer)
    return str_


def book_row(library: Library, book_id: str) -> str:
    book: Book = library.books[book_id]
    row: list[str] = []
    works: list[Work] = [library.works[work_id] for work_id in book.works]

    # Title
    colspan_title: int
    if len(works) == 1 and book.title == works[0].titles[book.language]:
        colspan_title = 2
    else:
        colspan_title = 1

    row.append(f"  <td colspan={colspan_title} rowspan={len(works)}>{book.title}</td>")
    if colspan_title == 1:
        row.append(f"  <td>{works[0].titles[book.language]}</td>")

    # Authors
    authors: list[set[str]] = []
    for work in works:
        authors.append(set(work.authors))
    rowspan_authors: int
    if all(authors_set == authors[0] for authors_set in authors):
        rowspan_authors = len(works)
    else:
        rowspan_authors = 1
    authors_str: str = " / ".join(
        [library.authors[author_id].name for author_id in works[0].authors]
    )
    row.append(f"  <td rowspan={rowspan_authors}>{authors_str}</td>")

    # Language
    row.append(f"  <td rowspan={len(works)}>{book.language}</td>")

    # Read status
    rowspan_read_status: int
    if book.fully_read or (not book.partial_read):
        rowspan_read_status = len(works)
    else:
        rowspan_read_status = 1
    read_status: str = "Lu" if works[0].read else "Pas Lu"
    row.append(f"  <td rowspan={rowspan_read_status}>{read_status}</td>")

    # Situation
    row.append(f"  <td rowspan={len(works)}>{book.situation}</td>")

    # Others rows if multiple works
    for i in range(1, len(works)):
        row.append("</tr>")
        row.append("<tr>")
        row.append(f"  <td>{works[i].titles[book.language]}</td>")
        if rowspan_authors == 1:
            authors_str = " / ".join(
                [library.authors[author_id].name for author_id in works[i].authors]
            )
            row.append(f"  <td>{authors_str}</td>")
        if rowspan_read_status == 1:
            read_status = "Lu" if works[i].read else "Pas Lu"
            row.append(f"  <td>{read_status}</td>")

    return "<tr>\n" + "\n".join(row) + "\n</tr>"


def works_table(library: Library, works_ids: set[str]) -> str:
    header: list[str] = [
        "<table>",
        "  <thead>",
        "    <tr>",
        "      <th>Titre</th>",
        "      <th>Titres alternatifs</th>",
        "      <th>Auteur·rice</th>",
        "      <th>Lu</th>",
        "      <th>Possédé</th>",
        "    </tr>",
        "  </thead>",
        "  <tbody>",
        "",
    ]
    sorted_works_ids: list[str] = library.sort_works_ids(works_ids)
    body: list[str] = [work_row(library, work_id) for work_id in sorted_works_ids]
    footer: list[str] = [
        "",
        "  </tbody>",
        "</table>",
    ]
    str_ = "\n".join(header) + textwrap.indent("\n".join(body), "    ") + "\n".join(footer)
    return str_


def work_row(library, work_id: str) -> str:
    work: Work = library.works[work_id]
    row: list[str] = []

    primary_language: str = "fr" if "fr" in work.titles else "en"
    vo_marker: str = " VO" if primary_language == work.language else ""
    title: str = f"{work.titles[primary_language]} ({primary_language}{vo_marker})"

    alt_titles: list = []
    for language, alt_title in work.titles.items():
        if language != primary_language:
            vo_marker = " VO" if language == work.language else ""
            alt_titles.append(f"{alt_title} ({language}{vo_marker})")
    if not alt_titles:
        alt_titles.append("")

    rowspan: int = len(alt_titles)

    # Title
    row.append(f"<td rowspan={rowspan}>{title}</td>")
    # Others titles
    row.append(f"<td>{alt_titles[0]}</td>")
    # Authors
    authors: str = " / ".join([library.authors[author_id].name for author_id in work.authors])
    row.append(f"<td rowspan={rowspan}>{authors}</td>")
    # Read status
    read_status: str = "Lu" if work.read else "Pas Lu"
    row.append(f"<td rowspan={rowspan}>{read_status}</td>")
    # Possédé
    owned: str = "Possédé" if work.owned else "Non possédé"
    row.append(f"<td rowspan={rowspan}>{owned}</td>")

    for i in range(1, len(alt_titles)):
        row += [
            "</tr>",
            "<tr>",
            f"<td>{alt_titles[i]}</td>",
        ]

    return "<tr>\n" + textwrap.indent("\n".join(row), "  ") + "\n</tr>"


def authors_table(library: Library, authors_ids: set[str], sorting: str = "name") -> str:
    header: list[str] = [
        "<table>",
        "  <thead>",
        "    <tr>",
        "      <th>Auteur·rice</th>",
        "      <th>Nombre oeuvres lues</th>",
        "      <th>Nombre oeuvres possédées</th>",
        "      <th>Nombre livres possédés</th>",
        "    </tr>",
        "  </thead>",
        "  <tbody>",
        "",
    ]
    sorted_authors_ids: list[str] = library.sort_authors_ids(authors_ids, sorting)
    body: list[str] = [author_row(library, author_id) for author_id in sorted_authors_ids]
    footer: list[str] = [
        "",
        "  </tbody>",
        "</table>",
    ]
    str_ = "\n".join(header) + textwrap.indent("\n".join(body), "    ") + "\n".join(footer)
    return str_


def author_row(library: Library, author_id: str) -> str:
    author: Author = library.authors[author_id]
    row: list[str] = [
        f"<td>{author.name}</td>",
        f"<td>{author.works_read}</td>",
        f"<td>{author.works_owned}</td>",
        f"<td>{author.books_owned}</td>",
    ]
    return "<tr>\n" + textwrap.indent("\n".join(row), "  ") + "\n</tr>"
