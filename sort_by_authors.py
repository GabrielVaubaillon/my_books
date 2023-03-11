# A data-line in the file is built this way :
# | Titre | Auteur(s) | Langue | ISBN | Possédé | Lu | Situation | Notes |


# Open the file, extract all the data
# -----------------------------------
f = open("possedes_ou_lus.md", "r")
lignes = f.readlines()
f.close()

header = lignes[:2]
# la derniere ligne est vide
data = [ l[:-1].split("|") for l in lignes[2:-1]]

# Sort books by authors. By the LASTNAME

def sorting_key(d):
    # Le nom de l'auteur
    tmp = d[2]

    # Si deux auteurs, on garde le premier
    if "&" in tmp:
        tmp = (tmp.split("&"))[0]

    # On enleve les espaces autours du nom
    tmp = tmp.strip(" ")

    # Les bouquins sans auteurs : à la fin
    if tmp == "":
        return "Zzzz"

    # On separe le prénom et le nom
    tmp = tmp.split(" ")

    # On garde le nom
    res = tmp[-1]
    return res

data = sorted(data, key=lambda x: sorting_key(x))



# Once data is sorted, rewrite it
f = open("sorted", "w")
f.write(header[0])
f.write(header[1])
for d in data:
    ch = ""
    for st in d[1:]:
        ch += "|"
        ch += st
    ch += "\n"
    f.write(ch)
f.close()
