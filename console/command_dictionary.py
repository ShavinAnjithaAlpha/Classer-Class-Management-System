def fetchCommandDict(query: str, split_key: str = "-", equal_key: str = "=") -> dict[str, str]:
    command_items = query.split(split_key)
    cmd_dict = {}
    for item in command_items[1:]:
        if equal_key in item:
            cmd_dict[item.split(equal_key)[0].strip()] = item.split(equal_key)[1].strip()
        else:
            cmd_dict[item.strip()] = None

    return cmd_dict

def checkCommand(cmd_dict : dict , *args) -> bool:

    for key in args:
        if key in cmd_dict.keys():
            return True
    return False

def printDict(result_dict : dict, header = "", footer = ""):

    print(header)
    [print(f"{key} : {value}") for key, value in result_dict.items()]
    print(footer)

def printDictList(dict_list : list[dict], header = "", footer = ""):

    print(header)
    if dict_list:
        for d in dict_list:
            printDict(d)
            print("")
    else:
        print("Nothing")
    print(footer)

def printList(list : list , header = "" , footer = "", steps = 5, sep = " "):

    print(header)
    for step , i in enumerate(list):
        print(i, sep=sep , end="")
        if step+1 % steps == 0:
            print("")
    print(footer)

if __name__ == "__main__":
    query = input("> ")
    print(fetchCommandDict(query))
