import data_management as dm

if __name__ == "__main__":
    filename = "../possedes_ou_lus.md"
    with open(filename, "r") as f:
        library = dm.list_from_md_file(f)
    library.sort()

    print(dm.HEADER, end="")
    for book in library:
        print(book.to_str())
    print()  # WHY !!?? why no empty line ? or is it ">" that get rid of the last empty line ?
