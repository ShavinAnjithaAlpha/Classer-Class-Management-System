import os, json5
import mysql.connector as mysql

from util.security.access import AccessManager
from util.logger import Logger

from console.student_cmd import StudentConsole
from console.class_cli import ClassCLI
from console.command_dictionary import printDict, printList, fetchCommandDict, checkCommand

from PyQt5.QtWidgets import QApplication
from dialog.admin_dialog import AdminDialog

if __name__ == "__main__":

    global accessManager, connection, logger

    print("////////////////////////////////////////////////////////")
    print("//////WELCOME TO CLASSER-CLASS MANAGEMENT SYSTEM///////")
    print("////////////////////////////////////////////////////////")
    if os.path.exists("settings"):
        with open(os.path.join("settings", "db_settings.json"), mode="r") as file:
            data = json5.load(file)

        try:
            connection = mysql.connect(host=data["host"], user=data["user"], password=data["password"],
                                       database=data["database"])
            logger = Logger(connection)
            # create access manager
            accessManager = AccessManager(connection)
            accessManager.attachLogger(logger)
            print("[INFO] database server connected successfully")
        except:
            print("[System Error] cannot initiate Access Manager")
            exit(1)


    else:
        # create the settings dir
        os.mkdir("settings")
        while True:
            # get connection parameters
            host = input("host: ")
            user = input("user: ")
            password = input("password: ")
            try:
                # first test the connection
                connection = mysql.connect(host=host, user=user, password=password)
            except Exception as ex:
                print(ex)
                continue

            if connection.is_connected():
                logger = Logger(connection) # initialize the global logger instance

                print("[INFO] database server connected successful")
                # save the database settings to json file
                with open(os.path.join("settings", "db_settings.json"), mode="w") as file:
                    data = {
                        "host": host,
                        "user": user,
                        "password": password,
                        "database": "classer"
                    }
                    json5.dump(data, file, indent=4)
                print("[INFO] settings file successfully created")

                # create Access Manager object globally
                accessManager = AccessManager(connection)
                accessManager.attachLogger(logger)
                accessManager.initializeSystem(host, user, password=password)

                accessManager.setDatabse("classer")

                # get admin data
                app = QApplication([])
                admin_dialog = AdminDialog(None, accessManager)
                admin_dialog.show()
                data = admin_dialog.exec_()
                app.exec_()

                print("[INFO] admin data successfully submitted")
                print("[SYSTEM] {}".format(data))

                break

            else:
                print("[WARNING] cannot connect to database server...")



    printDict(connection.fetch_eof_status())
    print(f"MySQL version  : {connection.get_server_version()}")
    printDict({"SERVER" : connection.server_host , "PORT" : connection.server_port , "CONNECTION ID": connection.connection_id},
              footer="---------------------------\n")

    # initialize the system services
    show_msg = ("-- logout for Logout from System"
                "\n-- create user [email] [username] [password] for create user")

    print("[SYSTEM] log to system")
    while True:
        _query = input("> ")

        if _query.startswith("log"):
            cmd_dict = fetchCommandDict(_query)
            if checkCommand(cmd_dict, "username", "password"):
                user, pw = cmd_dict.get("username"), cmd_dict.get("password")
            else:
                user = input("username: ").strip()
                pw = input("password: ").strip()

            level = accessManager.logToSystem(user, pw)
            if level:
                print("[SYSTEM] logged to system :)")

                while True:

                    query = input("> ")
                    if query == "logout":
                        # end the current session of system and all unsaved data store into database and logs
                        accessManager.endSession()
                        print("[INFO] successfully log out from system")
                        break
                    elif query.startswith("create user"):
                        try:
                            _email, _username, _pw = tuple(query.split(" ")[2:])
                        except IndexError as ex:
                            print(ex)
                            continue
                        # ask for admin authentication
                        if accessManager.adminAuthentication(input("admin password >>> ")):
                            if (not accessManager.isExistsByUsername(_username) and
                                    not accessManager.isExistsByEmail(_email) and
                                    not accessManager.isPasswordDuplicate(_pw)):
                                user_id = accessManager.createUser(_username, _email, _pw)
                            else:
                                print("[SYSTEM] username, email or password already exists :(")
                                continue

                            print("[SYSTEM] successfully created user under USER ID {}".format(user_id))
                            print(f"[SYSTEM] username : {_username}\nemail : {_email}\n")
                        else:
                            print(f"[SYSTEM] access denied for create user {_username} :(")

                    elif query.startswith("show users"):
                        if level == 1:
                            [print(*item, sep="   ") for item in accessManager.getUsers()]
                        else:
                            print("[SYSTEM] need admin access priviliage :(")
                    elif query.startswith("delete user"):
                        if level == 1:
                            try:
                                id = int(query.split(" ")[2])
                            except IndexError or TypeError as ex:
                                print(ex)
                                continue

                            if accessManager.deleteUser(id):
                                print(f"[SYSTEM] successfully delete user under USER Id {id}")
                            else:
                                print("[SYSTEM] delete user unsuccessful :(")
                        else:
                            print("[SYSTEM] need admin access priviliage :(")

                    elif query == "std manager":
                        std_manager = StudentConsole(connection, logger)
                        std_manager.run()

                    elif query == "cls manager":
                        cls_console = ClassCLI(connection, logger, accessManager)
                        cls_console.run()



            else:
                print("[SYSTEM] access denied to system :(")

        elif _query.startswith("exit"):
            print("[SYSTEM] exit from system...")
            exit(0)
        else:
            print("[SYSTEM] syntax error!")



    try:
        connection.close()
    except Exception as ex:
        print(ex)


