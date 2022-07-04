from util.manager.student_manager import StudentManager
from console.command_dictionary import fetchCommandDict, printList, checkCommand, printDict, printDictList

class StudentConsole:

    def __init__(self, connection , logger):
        self.connection = connection
        self.logger = logger

    def run(self):

        global std_manager
        std_manager = StudentManager(self.connection, self.logger)
        query = ""

        while not query == "exit":
            query = input("std manager > ")

            if query.startswith("add student"):
                details = fetchCommandDict(query)

                _result = std_manager.addStudent(details)
                if _result:
                    print("[STD MANAGER] student added successful :)")
                else:
                    print("[STD MANAGER] student added unsuccessful :(")
                    continue

            elif query.startswith("show students"):
                cmd_dict = fetchCommandDict(query)

                if cmd_dict.get("limit"):
                    results = std_manager.getStudents(limit=int(cmd_dict["limit"]))
                else:
                    results = std_manager.getStudents(labeled=True)
                printDictList(results, header="[STD MANAGER] fetching students...\nRESULTS:\n")

            elif query.startswith("update student"):
                cmd_dict = fetchCommandDict(query)

                if "id" and "key" and "value" in cmd_dict.keys():
                    std_id , key , value = int(cmd_dict["id"]), cmd_dict["key"], cmd_dict["value"]
                    result = std_manager.updateStudent(std_id, key, value)
                    if result:
                        print("[STD MANAGER] updated student successfully")
                        print("[STD MANAGER] set {} of student with ID {}".format(key, std_id))
                    else:
                        print("[STD MANAGER] updated unsuccessful :(")
                    continue

                print("[STD MANAGER] syntax error!" )

            elif query.startswith("search"):
                cmd_dict = fetchCommandDict(query)
                if checkCommand(cmd_dict, "key", "value"):
                    results = std_manager.searchStudentsFromKey(cmd_dict["key"], cmd_dict["value"])
                    printDictList(results, header="[STD MANAGER] SEARCH RESULTS : ")

            elif query.startswith("show from key"):
                cmd_dict = fetchCommandDict(query)
                if checkCommand(cmd_dict , "key"):
                    result = std_manager.getValuesFromKey(cmd_dict["key"])
                    printList(result , sep=", ")

            elif query == "exit":
                print("[STD MANAGER] exit from STD MANAGER")
                break

            else:
                print("[STD MANAGER] syntax error!")