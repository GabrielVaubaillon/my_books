#!/usr/bin/env python3
import data_management as dm
from check_file import check_file


def sort_library(file_in, file_out):
    print(f"Loadings books from file ({file_in})")
    with open(file_in, "r") as f:
        library = dm.list_from_md_file(f)

    print("Sorting books")
    library.sort()

    string = dm.HEADER
    for book in library:
        string += book.to_str() + "\n"

    print(f"Writing books in file ({file_out})")
    with open(file_out, "w") as f:
        f.write(string)
        f.write("\n")
    print("Sorting Done")


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

