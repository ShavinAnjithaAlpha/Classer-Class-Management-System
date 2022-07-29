import datetime

import mysql.connector as mysql
import mysql.connector.errors as err

from util.logger import Logger


class StudentManager:
    LOCATION = "student manager"

    STD_KEYS = {
        "username": ["username", "user_name"],
        "password": ["password"],
        "first_name": ["firstName", "fName", "firstname", "first_name"],
        "last_name": ["lastName", "lName", "lastname", "last_name"],
        "address": ["address", "adr", "Adr"],
        "sex": ["sex", "sexual"],
        "student_contact": ["student_contact", "telNum", "num", "TelNum", "telephoneNumber", "telephone_number"],
        "parent_contact": ["parent_contact", "parTelNum", "parNum", "parMobNum", "parent_mobile_number",
                           "parentMobileNumber"],
        "id": ["id", "index", "Index", "i", "ID"],
        "birthday": ["bDay", "birth_day", "birthday"],
        "added_at": ["eDay", "enteredDay", "enter_day", "entered_day", "eday"],
        "school": ["school", "sch", "Sch"],

    }

    LABELED_KEYS = {
        "id": "Student ID",
        "username": "Username",
        "password": "Password",
        "first_name": "First Name",
        "last_name": "Last Name",
        "address": "Address",
        "school": "School",
        "birthday": "Birthday",
        "sex": "Sex",
        "student_contact": "Student Contact Number",
        "parent_contact": "Parent Contact Number",
        "added_at": "Registered At",

    }

    @staticmethod
    def getKey(text: str):
        for key in StudentManager.STD_KEYS.keys():
            if (text.lower() in StudentManager.STD_KEYS.get(key)):
                return key

        return None

    def __init__(self, connection: mysql.MySQLConnection, logger: Logger, *args, **kwargs) -> None:
        self.connection = connection
        self.logger = logger

    def addStudent(self, details: dict) -> int:

        # update the details dictionary
        _details = {}
        for key, value in details.items():
            _details[self.getKey(key)] = details.get(key, None)
        details = _details

        details["added_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # process database query
        cursor = self.connection.cursor()
        add_student_query = """INSERT INTO students(username, password, first_name, last_name, address, school, birthday,
                                                    student_contact, parent_contact, sex, added_at)
                            VALUES (%(username)s, %(password)s, %(first_name)s, %(last_name)s, %(address)s, %(school)s, %(birthday)s,
                                    %(student_contact)s, %(parent_contact)s, %(sex)s, %(added_at)s)"""

        try:
            cursor.executemany(add_student_query, (details,))
            std_id = cursor.lastrowid
            self.connection.commit()
            cursor.close()
            # log the event
            self.logger.event(location=self.LOCATION, content="student added to database", student_id=std_id,
                              student_name=f"{details['first_name']} {details['last_name']}")

            return std_id
        except mysql.Error as ex:
            cursor.close()
            # log error
            self.logger.error(location=self.LOCATION, mysql_error=str(ex), content="student add unsuccessful")

            raise ex

    def fetchStudentsWithKeys(self, search_query: str, labeled=False, params: tuple = None, limit: int = None) -> list[
        dict]:

        cursor = self.connection.cursor(dictionary=True)

        cursor.execute(search_query, params=params)
        # fetch the results
        if limit:
            student_list = cursor.fetchmany(limit)
        else:
            student_list = cursor.fetchall()

        # log the event
        self.logger.info(location=self.LOCATION, content="searching for students",
                         result_count=cursor.rowcount)
        # reset and close the cursor
        cursor.reset()
        cursor.close()

        if labeled:
            _student_list = []
            for student in student_list:
                _std = {}
                for key in student.keys():
                    # rename the keys of student dictionary
                    _std[self.LABELED_KEYS[key]] = student.get(key)
                _student_list.append(_std)
            del student_list
            return _student_list
        else:
            return student_list

    def searchStudentByName(self, name: str, labeled=False, limit: int = None, order="id") -> list[dict]:

        student_search_query = "SELECT * FROM students WHERE first_name LIKE '%{}%' OR last_name LIKE '%{}%' ORDER BY {}".format(
            name, name, order
        )
        return self.fetchStudentsWithKeys(student_search_query, labeled, limit=limit)

    def getStudentByUsername(self, username: str, labeled=False, limit: int = None) -> dict:

        student_search_query = "SELECT * FROM students WHERE username = %s"
        std = self.fetchStudentsWithKeys(student_search_query, labeled, params=(username,), limit=limit)
        if std == []:
            return None
        else:
            return std[0]

    def getStudentById(self, std_id: int) -> dict:

        student_query = "SELECT * FROM students WHERE id = %s LIMIT 1"
        try:
            return self.fetchStudentsWithKeys(student_query, params=(std_id,))[0]
        except mysql.Error as ex:
            self.logger.error(location=self.LOCATION, mysql_error=str(ex),
                              content="try to get student details with invalid student ID")
            return None

    def searchStudentsFromKey(self, key: str, value, labeled=False, limit: int = None) -> list[dict]:

        _key = self.getKey(key)
        if _key:
            search_query = "SELECT * FROM students WHERE {} LIKE %s ".format(_key)
            return self.fetchStudentsWithKeys(search_query, labeled, params=('%{}%'.format(value),), limit=limit)
        return []

    def getStudents(self, labeled=False, limit: int = None, order="id") -> list[dict]:

        search_query = "SELECT * FROM students ORDER BY %s"
        return self.fetchStudentsWithKeys(search_query, labeled, params=(order,), limit=limit)

    def getValuesFromKey(self, key: str, order: str = "id", limit: int = None) -> list:

        _key = self.getKey(key)
        if _key:
            cursor = self.connection.cursor()

            search_query = "SELECT {} FROM students ORDER BY %s".format(_key)
            cursor.execute(search_query, (order,))

            if limit:
                result_set = cursor.fetchmany(limit)
            else:
                result_set = cursor.fetchall()
            # log the activity
            self.logger.info(location=self.LOCATION, content=f"request {_key} field data from students data",
                             result_count=cursor.rowcount)
            # return the one dimension list of values
            return [item[0] for item in result_set]
        return []

    def updateStudent(self, std_id: int, key: str, new_value) -> bool:

        _key = self.getKey(key)
        std_id = int(std_id)
        if not self.getStudentById(std_id):
            self.logger.warning(location=self.LOCATION,
                                content=f"try to update student with invalid student id : {std_id}")
            return False

        if _key:

            cursor = self.connection.cursor()

            update_query = "UPDATE students SET {} = %s WHERE id = %s".format(_key)
            try:
                cursor.execute(update_query, (new_value, std_id))
                # log the event
                self.logger.event(location=self.LOCATION, content="update a student",
                                  updated_field=_key)
                self.connection.commit()
                return True
            except mysql.Error as ex:
                cursor.close()
                # log the error
                self.logger.error(location=self.LOCATION, content=f"update student failed with student ID {std_id}",
                                  mysql_error=str(ex))
                return False

        return False

    def isStudentUserExists(self, username: str) -> bool:

        cursor = self.connection.cursor()

        find_query = "SELECT username FROM students WHERE username = %s LIMIT 1"
        cursor.execute(find_query, (username,))

        result_set = cursor.fetchone()
        cursor.close()

        return result_set

    def isPasswordDuplicate(self, password: str) -> bool:

        cursor = self.connection.cursor()

        find_query = "SELECT username FROM students WHERE password = %s LIMIT 1"
        cursor.execute(find_query, (password,))

        result_set = cursor.fetchone()
        cursor.close()

        return result_set

    def count(self, count_query: str) -> int:

        cursor = self.connection.cursor()

        cursor.execute(count_query)
        count = cursor.fetchone()[0]
        cursor.close()

        return count

    def studentCount(self) -> int:
        """

        :return: total student count of database
        """
        return self.count("SELECT COUNT(id) FROM students")

    def lastMonthStudentCount(self) -> int:
        """

        :return: total number of students those register in last month
        """
        today = datetime.datetime.now().strftime("%Y-%m-")
        return self.count(f"SELECT COUNT(id) FROM students WHERE added_at LIKE '{today}%' ")

    def lastDayStudentCount(self) -> int:
        """

        :return: total number of student those registered today
        """

        today = datetime.datetime.now().strftime("%Y-%m-%d")
        return self.count(f"SELECT COUNT(id) FROM students WHERE added_at LIKE '{today}%' ")

    def getResult(self, query: str) -> list:

        cursor = self.connection.cursor()
        cursor.execute(query)

        result = cursor.fetchall()
        cursor.close()
        return result

    def countByDate(self, date: datetime.datetime):

        return self.count(f"SELECT COUNT(id) FROM students WHERE added_at LIKE f'{date.strftime('%Y-%m-%d')}%' ")

    def lastYear(self, option: str = "day") -> list:

        if option == "day":
            return self.getResult(
                "SELECT COUNT(id) , CAST(added_at AS DATE) FROM students WHERE YEAR(added_at) = YEAR(CURRENT_DATE) GROUP BY CAST(added_at AS DATE )")
        else:
            return self.getResult(
                "SELECT COUNT(id) , MONTH(added_at), YEAR(added_at) FROM students WHERE YEAR(added_at) = YEAR(CURRENT_DATE) GROUP BY CAST(added_at AS DATE )")

    def lastMonth(self) -> list:

        return self.getResult(
            "SELECT COUNT(id) , CAST(added_at AS DATE) FROM students WHERE MONTH(added_at) = MONTH(CURRENT_DATE) GROUP BY CAST(added_at AS DATE )")

    def countByGroup(self, option: str = "day") -> list:

        if option == "day":
            return self.getResult(
                "SELECT COUNT(id) , CAST(added_at AS DATE) FROM students GROUP BY CAST(added_at AS DATE)")
        else:
            return self.getResult(
                "SELECT COUNT(id) , MONTH(added_at), YEAR(added_at) FROM students GROUP BY CAST(added_at AS DATE)")

    # static method for use by another modules of the system with shared connection
    @staticmethod
    def ensureStudents(connection: mysql.MySQLConnection, std_list: list[int]) -> bool:

        cursor = connection.cursor()
        check_query = "SELECT id FROM students WHERE id = %s"

        for std_id in std_list:
            cursor.execute(check_query, (std_id,))
            if not cursor.fetchall():
                cursor.close()
                return False

        cursor.close()
        return True

    @staticmethod
    def getStudentNames(connection: mysql.MySQLConnection, std_list: list[int]) -> list[dict]:

        cursor = connection.cursor(dictionary=True)
        name_query = "SELECT id, first_name, last_name FROM students WHERE id = %s"

        cursor.executemany(name_query, [(std_id,) for std_id in std_list])
        result = cursor.fetchall()

        cursor.close()
        return result
