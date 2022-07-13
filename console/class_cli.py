import datetime

import mysql.connector as mysql
from util.logger import Logger
from util.security.access import AccessManager

from util.manager.class_engine import ClassEngine
from  util.manager.class_manager import ClassManager

from console.command_dictionary import printDictList, printDict, printList , fetchCommandDict

def checkAdminQuery(query : str) -> bool:

    for q in ClassCLI.admin_query:
        if query.startswith(q):
            return True
    return False

class ClassCLI:

    admin_query = [
        "create class",
        "add time",
        "change time",
        "change class name",
        "change class fee",
        "change class description"
    ]

    def __init__(self ,connection : mysql.MySQLConnection , logger : Logger, accessManager : AccessManager):
        self.connection : mysql.MySQLConnection = connection
        self.accessManager = accessManager
        self.logger : Logger = logger

    def run(self):

        # create class engine and class manager instance
        class_engine = ClassEngine(self.connection, self.logger)
        class_manager = ClassManager(self.connection , self.logger)

        while True:
            query = input("cls manager > ")

            if checkAdminQuery(query) and not self.accessManager.session["level"] == 1:
                print("[CLASS MANAGER] access denied. admin access priviliage needed")
                continue

            if query.startswith("create class"):
                cmd_dict = fetchCommandDict(query)
                try:
                    cmd_dict["grade"] = int(cmd_dict["grade"])
                    cmd_dict["fees"] = float(cmd_dict["fees"])
                    print(cmd_dict)

                    result = class_engine.createClass(cmd_dict)
                    if not result == -1:
                        print("[CLASS MANAGER] create class successful.")
                        print("[CLASS MANAGER] class ID : " , result)
                    else:
                        print("[CLASS MANAGER] something wrong happened :(")
                        continue
                except Exception as ex:
                    print(ex)
                    continue

            elif query.startswith("add time"):

                cls_id = int(input("class ID: "))
                day_of_week = int(input("day of week: "))
                start_time = datetime.time.fromisoformat(input("start time: "))
                end_time = datetime.time.fromisoformat(input("end time: "))

                result = class_engine.addTimes(cls_id, day_of_week, start_time, end_time)
                if result:
                    print("[CLASS MANAGER] add time successful")
                else:
                    print("[CLASS MANAGER] something went wrong! :(")
                    continue

            elif query.startswith("change class name"):
                pass

            elif query.startswith("show classes"):
                result = class_manager.getClasses()
                printDictList(result, header="RESULT:\n")

            elif query.startswith("show times"):
                cmd_list = fetchCommandDict(query)

                if cmd_list.get("cls_id"):
                    result = class_manager.getTimesByClassId(int(cmd_list.get("cls_id")))
                    printDictList(result, header="RESULT:\n")
                elif cmd_list.get("day"):
                    result = class_manager.getClassWithDayOfWeek(int(cmd_list.get("day")))
                    printDictList(result , header="RESULT:\n")


            elif query.startswith("exit"):
                break

            else:
                print("[CLASS MANAGER] syntax error!")

