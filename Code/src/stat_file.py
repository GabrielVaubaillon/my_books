from pathlib import Path
import re

from library import Language


def percent(number: int, total: int):
    if number == 0:
        return "0"
    if number == total:
        return f"{number} (100%)"
    return f"{number} ({round(number/total*100, 2)}%)"


def write_stat_file(
    collections: dict[str, set[str]],
    collections_files_dir: Path,
    output_file: Path,
    lang: dict[str, Language],
    owned_languages: list[str],
    situations: list[str],
):
    assert collections_files_dir.is_dir()
    stats: dict[str, int] = {name: len(collection) for name, collection in collections.items()}
    root_dir: Path = output_file.parent
    collections_relative_path: Path = collections_files_dir.relative_to(root_dir)

    owned_w: int = stats["owned_w"]
    owned_b: int = stats["owned_b"]

    lines: list[str] = [
        "# Mes livres - Lus et possédés",
        "",
        "Les liens donnent accès au tableau détaillé correspondant.",
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
        "## Ma bibliothèque",
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
        f"{percent(stats["owned_w_a"], stats["all_a"])}, trié·e·s par "
        f"[nombre d'oeuvres]({collections_relative_path}/owned_w_a.md)"
        " ou par "
        f"[nombre de livres]({collections_relative_path}/owned_b_a.md)"
        " possédés."
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
        f"- Toutes les oeuvres: [{stats["all_w"]}]({collections_relative_path}/all_w.md)",
        f"- Tous les auteur·rice·s: [{stats["all_a"]}]({collections_relative_path}/all_a.md)",
    ]

    file_content: str = "\n".join(lines)
    # Remove links to inexitent files (when 0 elements in it)
    file_content = re.sub(r"\[0]\(.*?\.md\)", "0", file_content)

    root_dir.mkdir(parents=True, exist_ok=True)
    with open(output_file, mode="w", encoding="utf-8") as file:
        file.write(file_content)
