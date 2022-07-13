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
                            
            CREATE TABLE students(
                            id INT AUTO_INCREMENT UNIQUE PRIMARY KEY NOT NULL ,
                            username VARCHAR(150) UNIQUE NOT NULL ,
                            password VARCHAR(150) UNIQUE NOT NULL ,
                            first_name TEXT NOT NULL ,
                            last_name TEXT NOT NULL ,
                            address TEXT NOT NULL ,
                            school TEXT,
                            birthday DATE NOT NULL ,
                            sex ENUM('male', 'female', 'other') NOT NULL ,
                            student_contact VARCHAR(13),
                            parent_contact VARCHAR(13) NOT NULL,
                            added_at DATETIME NOT NULL 
                        );
                        
            CREATE TABLE classes(
                            id INTEGER AUTO_INCREMENT UNIQUE PRIMARY KEY NOT NULL ,
                            class_name VARCHAR(250) UNIQUE NOT NULL,
                            description TEXT DEFAULT NULL,
                            subject VARCHAR(150) NOT NULL ,
                            grade INT NOT NULL ,
                            payment_method ENUM("DAILY", "MONTHLY") NOT NULL DEFAULT "MONTHLY",
                            fees DOUBLE NOT NULL ,
                            started_at DATE NOT NULL,
                            available BOOLEAN NOT NULL DEFAULT TRUE
            );
            
            
            CREATE TABLE class_times(
                            id INTEGER AUTO_INCREMENT UNIQUE PRIMARY KEY NOT NULL ,
                            class_id INTEGER NOT NULL,
                            day_of_week SMALLINT NOT NULL,
                            start_time TIME NOT NULL ,
                            end_time TIME NOT NULL ,
                        
                            FOREIGN KEY (class_id) REFERENCES classes(id)
                        );
                        
            CREATE TABLE class_instance(
                            id INTEGER AUTO_INCREMENT UNIQUE PRIMARY KEY NOT NULL ,
                            class_id INTEGER NOT NULL ,
                            year INTEGER NOT NULL ,
                            students TEXT NOT NULL ,
                            started_at DATE NOT NULL ,
                            initial_count INTEGER NOT NULL ,
                            current_count INTEGER NOT NULL ,
                            finished BOOLEAN NOT NULL DEFAULT FALSE,
                            ended_at DATE,
                        
                            FOREIGN KEY (class_id) REFERENCES classes(id)
                        );

            
    
    """

    LOG_FILES = [
        "warnings.log",
        "error.log",
        "debug.log",
        "info.log",
        "event.json"
    ]


    def __init__(self, connection = None):
        self.connection : mysql.MySQLConnection = connection

        # create empty session dict
        self.session = {}

    def setConnection(self, connection : mysql.MySQLConnection) -> None:
        self.connection = connection


    def setDatabse(self, databse : str) -> None:

        if self.connection is not None:
            self.connection.database = databse

    def attachLogger(self, logger : Logger) -> None:

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
            connection.commit()
            cursor.close()
            connection.close()

        else:
            raise ConnectionError("Cannot be connected to the Database Server! Please try again!")

    def saveAdminData(self, data_dict : dict) -> None:

        # get the cursor object using connection
        cursor = self.connection.cursor()

        admin_text_query = "INSERT INTO settings(field, text_value) VALUES (%s, %s)"
        admin_int_query = "INSERT INTO settings(field, number_value) VALUES (%s, %s)"
        admin_float_query = "INSERT INTO settings(field, float_value) VALUES (%s, %s)"
        admin_bool_query = "INSERT INTO settings(field, bool_value) VALUES (%s, %s)"

        try:
            for field , value in data_dict.items():
                # save there values based on  its types
                if isinstance(value, str):
                    cursor.execute(admin_text_query, (field, value))
                elif isinstance(value, int):
                    cursor.execute(admin_int_query, (field, value))
                elif isinstance(value, float):
                    cursor.execute(admin_float_query, (field, value))
                elif isinstance(value, bool):
                    cursor.execute(admin_bool_query, (field, value))

            # save the changes
            self.connection.commit()
            cursor.close()

        except mysql.errors as ex:
            cursor.close()
            raise ex


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

        cursor.execute(auth_query, ("password", ))
        admin_pw = cursor.fetchone()[0]

        cursor.close()
        # check whether password is correct or not
        return admin_pw == password

    def logToSystem(self, username : str, password : str) -> int:

        cursor = self.connection.cursor()

        # get admin username and password using setting table
        admin, admin_pw = None, None
        admin_query = "SELECT text_value FROM settings WHERE field = %s LIMIT 1"

        cursor.execute(admin_query, ["username",] )
        admin = cursor.fetchone()[0]

        cursor.execute(admin_query, ["password", ])
        admin_pw = cursor.fetchone()[0]

        # get user password under given username if the user exists
        user_query = "SELECT id, password FROM users WHERE username = %s LIMIT 1"
        cursor.execute(user_query , [username, ])

        user_id, user_pw = None, None
        user_data = cursor.fetchone()
        if user_data:
            user_id, user_pw = tuple(user_data)
        cursor.close()

        # checking usernames and given passwords for matching
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

    def getUsers(self) -> list[list[str]]:

        cursor = self.connection.cursor()
        user_get_query = "SELECT id, username, email, created_at FROM users ORDER BY id"

        cursor.execute(user_get_query)
        users_data = cursor.fetchall()

        cursor.close()
        return users_data

    def deleteUser(self, user_id : int) -> bool:

        cursor = self.connection.cursor()

        user_delete_query = "DELETE FROM users WHERE id = %s"
        try:
            cursor.execute(user_delete_query, (user_id, ))
            cursor.close()
            return True
        except Exception as ex:
            print(ex)
            cursor.close()
            return False

    def isExists(self, key : str , value : str) -> bool:

        cursor = self.connection.cursor()
        user_exists_query = f"SELECT * FROM users WHERE {key} = %s LIMIT 1"

        cursor.execute(user_exists_query, (value,))
        if not cursor.fetchone():
            cursor.close()
            return False
        else:
            cursor.close()
            return True

    def isExistsByUsername(self, username : str) -> bool:

        return self.isExists("username", username)

    def isExistsByEmail(self, email : str) -> bool:

        return self.isExists("email", email)

    def isPasswordDuplicate(self, password : str) -> bool:

        return self.isExists("password", password)

    def endSession(self):

        # end the session with save session data to sessions table
        cursor = self.connection.cursor()
        session_query = "INSERT INTO sessions(user_id, level, start_at, end_at) VALUES (%s, %s, %s, %s)"
        if self.session["level"] == 1:
            level = "Admin"
        else:
            level = "User"

        cursor.execute(session_query,
                       (self.session["user_id"], level,
                        self.session["started_at"].strftime("%Y-%m-%d %H:%M:%S") ,
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                       )

        session_id = cursor.lastrowid
        # cached the log files to database
        self.logger.flush() # flush the un stored log buffers
        self.logger.passEventsToServer(session_id)
        self.logger.freeUpCache(session_id)

        self.connection.commit()
        cursor.close()
        # # finally close the connection
        # self.connection.close()