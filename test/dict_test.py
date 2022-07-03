d = {
    "sex" : "male",
    "bday" : "2022-1-5",
    "year":  2022
}

for key in d.keys():
    d[key.capitalize()] = d.pop(key)

print(d)