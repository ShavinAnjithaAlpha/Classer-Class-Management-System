
def dict_str(details_dict : dict) -> str:

    dict_text = ""

    for key, value in details_dict.items():
        dict_text += f"{key} : {value}\n"

    return dict_text