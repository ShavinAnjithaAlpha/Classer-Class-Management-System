import os, json5
import mysql.connector as mysql

from util.security.access import AccessManager

if __name__ == "__main__":

    global accessManager, connection

    if os.path.exists("settings"):
        with open(os.path.join("settings", "db_settings.json"), mode="r") as file:
            data = json5.load(file)

        try:
            connection = mysql.connect(host=data["host"], user=data["user"], password=data["password"],
                                       database=data["database"])
            # create access manager
            accessManager = AccessManager(connection)
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
                accessManager.initializeSystem(host, user, password=password)

                accessManager.setDatabse("classer")
                break

            else:
                print("[WARNING] cannot connect to database server...")

    print(connection.fetch_eof_status())
    print(connection.server_host, connection.server_port, connection.get_server_info(), connection.get_server_version())

    # log to the system now
    user = input("username: ")
    pw = input("password: ")

    level = accessManager.logToSystem(user, pw)
    if level:
        print("[SYSTEM] log to system :)")
    else:
        print("[SYSTEM] access denied to system :(")