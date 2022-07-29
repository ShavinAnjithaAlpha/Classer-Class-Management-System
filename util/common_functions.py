import json5

ACCESS_FILE = "access_levels.json"


def dict_str(details_dict: dict) -> str:
    dict_text = ""

    for key, value in details_dict.items():
        dict_text += f"{key} : {value}\n"

    return dict_text


def getAccessIndexes(level=0, section_id: int = 0, file=ACCESS_FILE):
    with open(file) as file:
        data = json5.load(file)

    # filter the data
    results = []
    if level:
        for item in data:
            if "." in item[0]:
                a, b = tuple(map(int, item[0].split(".")))
                if a == section_id:
                    results.append((b, item[1], item[2]))
    else:
        for item in data:
            if not "." in item[0]:
                results.append((int(item[0]), item[1], item[2]))

    return results


def checkAccessPreviliage(indexes: list, section: int, access_level: int) -> bool:
    for item in indexes:
        if item[0] == section:
            if access_level == 1:
                return item[1]
            else:
                return item[2]
    return True


if __name__ == "__main__":
    print(getAccessIndexes(1, 1))
