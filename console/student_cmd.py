from util.manager.student_manager import StudentManager

class StudentConsole:

    def __init__(self, connection , logger):
        self.connection = connection
        self.logger = logger

    def run(self):

        global std_manager
        std_manager = StudentManager(self.connection, self.logger)
        query = input("std_manager >>> ")

        while not query == "exit":
            if query.startswith("add student"):
                items = query.split(" ")[2:]

                details = {}
                for item in items:
                    key , value = item.split("=")
                    details[key] = value

                _result = std_manager.addStudent(details)
                if _result:
                    print("[STD MANAGER] student added successful :)")
                else:
                    print("[STD MANAGER] student added unsuccessful :(")
                    continue

            elif query == "show students":
                results = std_manager.getStudents(labeled=True)
                print("[STD MANAGER] fetching students...\nRESULTS:\n")
                print(*results, sep="\n")

            elif query == "exit":
                print("[STD MANAGER] exit from STD MANAGER")
                break
            query = input("std manager >>> ")