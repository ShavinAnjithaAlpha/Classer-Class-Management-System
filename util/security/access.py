import datetime
import os

import mysql.connector as mysql

from util.logger import Logger

class AccessManager:

    database_create_query = """
            
            DROP DATABASE IF EXISTS classer;
            CREATE DATABASE classer;
            USE classer;
            
            CREATE TABLE settings(field VARCHAR(150) NOT NULL PRIMARY KEY ,
                                    text_value MEDIUMTEXT,
                                    number_value INTEGER,
                                    bool_value BOOLEAN,
                                    float_value FLOAT);
            
            CREATE TABLE users(id INT AUTO_INCREMENT UNIQUE PRIMARY KEY NOT NULL ,
                                username VARCHAR(100) UNIQUE NOT NULL ,
                                password VARCHAR(100) UNIQUE NOT NULL ,
                                email VARCHAR(200) UNIQUE NOT NULL ,
                                created_at DATETIME NOT NULL ,
                                updated_at DATETIME);
            
            CREATE TABLE sessions(id INT AUTO_INCREMENT UNIQUE PRIMARY KEY NOT NULL ,
                                    user_id INT NOT NULL,
                                    level ENUM('Admin', 'User') NOT NULL ,
                                    start_at DATETIME NOT NULL ,
                                    end_at DATETIME NOT NULL,
            
                                    FOREIGN KEY (user_id) REFERENCES users(id));
            
            CREATE TABLE events(id INTEGER AUTO_INCREMENT UNIQUE PRIMARY KEY NOT NULL ,
                            session_id INT NOT NULL,
                            time TIMESTAMP NOT NULL ,
                            content LONGTEXT,
            
                            FOREIGN KEY (session_id) REFERENCES sessions(id));
            
            CREATE TABLE logs(session_id INT NOT NULL ,
                            level VARCHAR(25) NOT NULL ,
                            content LONGTEXT,
                            
                            FOREIGN KEY (session_id) REFERENCES sessions(id)
                            );
            
    
    """

    LOG_FILES = [
        "warnings.log",
        "error.log",
        "debug.log",
        "info.log"
    ]


    def __init__(self, connection = None):
        self.connection : mysql.MySQLConnection = connection

        # create empty session dict
        self.session = {}

    def setConnection(self, connection : mysql.MySQLConnection):
        self.connection = connection


    def setDatabse(self, databse : str):

        if self.connection is not None:
            self.connection.database = databse

    def attachLogger(self, logger : Logger):

        self.logger = logger

    @staticmethod
    def initializeSystem(server : str = "localhost" ,user : str = "root", *, password : str ) -> None:

        # create the database , folder structure and other files
        # set up the database connection and configurations

        # first connect to the database and get the connection instance
        connection = mysql.connect(host = server , user = user, password = password)
        if connection.is_connected():
            # do all database operation for system initializing
            cursor = connection.cursor()

            cursor.execute(AccessManager.database_create_query)
            # create the log directories
            if not os.path.exists("log"):
                os.mkdir("log")

                # inside the log dir created main cached log files
                for file in AccessManager.LOG_FILES:
                    with open(os.path.join("log", file), mode="w") as log_file:
                        pass

            # commit the changes to the database
            # connection.commit()
            cursor.close()
            connection.close()

        else:
            raise ConnectionError("Cannot be connected to the Database Server! Please try again!")

    def getAdminData(self, data_dict : dict) -> None:

        # get the cursor object using connection
        cursor = self.connection.cursor()

        admin_query = "INSERT INTO settings(field, text_value) VALUES (%s, %s)"

        cursor.executemany(admin_query, data_dict.items())
        # save the changes
        self.connection.commit()
        cursor.close()

    def createUser(self, username : str, email : str , password : str) -> int:

        cursor = self.connection.cursor()

        user_create_query = " INSERT INTO users(username, email, password, created_at) VALUES(%s, %s, %s, %s) "
        cursor.execute(user_create_query, (username, email, password, datetime.datetime.now()))
        self.connection.commit()

        user_id =  cursor.lastrowid

        cursor.close()
        return user_id

    def adminAuthentication(self, password : str) -> bool:

        cursor = self.connection.cursor()
        auth_query = "SELECT text_value FROM settings WHERE field = %s LIMIT 1"

        cursor.execute(auth_query, ("password"))
        cursor.close()
        # check whether password is correct or not
        return cursor.fetchone()[0] == password

    def logToSystem(self, username : str, password : str) -> int:

        cursor = self.connection.cursor()

        admin_query = "SELECT text_value FROM settings WHERE field = %s LIMIT 1"
        cursor.executemany(admin_query, [["username",] , ["password"]])

        admin, admin_pw = None, None
        admin_field = cursor.fetchone()
        if admin_field:
            admin, admin_pw = tuple(admin_field)

        user_query = "SELECT id, password FROM users WHERE username = %s LIMIT 1"
        cursor.execute(user_query , [username, ])

        user_id, user_pw = None, None
        user_data = cursor.fetchone()
        if user_data:
            user_id, user_pw = tuple(user_data)
        cursor.close()

        if (admin is not None and admin_pw is not None) and (username == admin and password == admin_pw):
            self.session["level"] = 1
            self.session["user_id"] = -1
            self.session["started_at"] = datetime.datetime.now()

            return 1 # for admin access
        elif user_pw is not None and password == user_pw:
            self.session["level"] = 2
            self.session["user_id"] = user_id
            self.session["started_at"] = datetime.datetime.now()

            return 2 # for user access
        else:
            return 0

    def endSession(self):

        # end the session with save session data to sessions table
        cursor = self.connection.cursor()
        session_query = "INSERT INTO sessions(user_id, level, start_at, end_at) VALUES (%d, %s. %s, %s)"
        cursor.execute(session_query,
                       (self.session["user_id"], self.session["level"], self.session["started_at"] ,datetime.datetime.now()))

        session_id = cursor.lastrowid
        # cached the log files to database
        self.logger.passEventsToServer(session_id)
        self.logger.freeUpCache(session_id)

        self.connection.commit()
        cursor.close()
        # finally close the connection
        self.connection.close()