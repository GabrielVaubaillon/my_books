import re

filename = "../possedes_ou_lus.md"

def main():
    return_value = 0
    with open(filename, "r") as f:
        lines = f.readlines()
    lines = [line[:-1] for line in lines]  # Get rid of \n
    if len(lines[-1]) > 0:
        print("No empty line at the end of the file")
        return 1
    lines = lines[:-1]

    columns_pattern = re.compile(r"""^\|( [^|]*\|){8}$""")

    # Check no trailing space and right number of columns
    for i, line in enumerate(lines):
        if not (re.match(columns_pattern, line)):
            print(f"{i+1}: not right number of columns or wrong space pattern {line}")
            return_value = 1
    if return_value != 0:
        return return_value

if __name__ == "__main__":
    main()
