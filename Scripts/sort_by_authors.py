import argparse
import data_management as dm
from check_file import check_file


def sort_library(file_in, file_out):
    with open(file_in, "r") as f:
        library = dm.list_from_md_file(f)

    library.sort()

    string = dm.HEADER
    for book in library:
        string += book.to_str() + "\n"

    with open(file_out, "w") as f:
        f.write(string)
        f.write("\n") # Jcomprend pas ou passe la ligne vide a lafin a chaque fois


if __name__ == "__main__":
    import os
    script_dir = os.path.abspath(os.path.dirname(__file__))
    f_in = os.path.join(script_dir, "../possedes_ou_lus.md")
    f_out = os.path.join(script_dir, "../possedes_ou_lus.md")

    res = check_file(f_in)

    if res == 0:
        sort_library(f_in, f_out)
        print("file sorted")

        check_file(f_out)

