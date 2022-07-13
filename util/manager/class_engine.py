import json5
import mysql.connector as mysql
from util.logger import Logger
from util.time_engine import DateTimeUtil

from util.common_functions import dict_str

import datetime

LOCATION = "CLASS ENGINE"

STD_KEYS = {
    "id": ["id", "index", "class_id", "cls_id", "cls id", "class id"],
    "class_name": ["class_name", "class name", "class-name", "cls_name", "cls name"],
    "description": ["description", "des"],
    "grade": ["grade", "gr"],
    "subject": ["subject", "sub"],
    "payment_method": ["payment_method", "payment method"],
    "fees": ["fees", "payment_cost", "payment cost"],
    "started_at": ["started_at", "started at", "started_date", "started_date"],
    "available": ["available", "current_status", "status", "current status"]
}

class ClassEngine:


    def __init__(self, connection : mysql.MySQLConnection , logger : Logger):
        self.connection : mysql.MySQLConnection = connection
        self.logger : Logger = logger

    @staticmethod
    def getKey(text: str):
        for key in STD_KEYS.keys():
            if (text.lower() in STD_KEYS.get(key)):
                return key

        return None

    def createClass(self, class_detail : dict) -> int:

        # update the details dictionary
        _details = {}
        for key, value in class_detail.items():
            _details[self.getKey(key)] = class_detail.get(key, None)
        class_details = _details

        # add the extra fields to detail dictionary
        class_details["started_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not class_details.get("description"):
            class_details["description"] = None

        # process the query
        cursor = self.connection.cursor()
        class_add_query = ("INSERT INTO classes"
                           "(class_name, description , subject, grade, payment_method, fees, started_at)"
                           " VALUES (%(class_name)s, %(description)s , %(subject)s , %(grade)s , %(payment_method)s , %(fees)s, %(started_at)s  )")

        try:
            cursor.executemany(class_add_query , (class_details, ))
            cls_id = cursor.lastrowid
            self.connection.commit()
            # close the cursor
            cursor.close()
            # log the event
            self.logger.event(location = LOCATION , content = f"create class with class ID {cls_id}", class_details = class_details)
            # return the class id
            return cls_id

        except mysql.Error as ex:
            # close the cursor
            cursor.close()
            # log the error
            self.logger.error(location = LOCATION , content = "error occured when created a class", mysql_error = ex.__str__() , class_details = class_details)
            return -1 # for invalid class ID

    def getClassTimes(self) ->tuple[dict]:

        time_query = "SELECT * FROM class_times ORDER BY day_of_week"
        cursor = self.connection.cursor(dictionary=True)

        cursor.execute(time_query)
        result = cursor.fetchall()

        cursor.close()
        return result

    def changeFees(self, cls_id : int , new_fees : float) -> bool:

        if not self.isClassExist(cls_id):
            self.logger.warning(location = LOCATION , content = f"try to change fees of invalid class with id : {cls_id}")
            return False

        cursor = self.connection.cursor()
        fees_query = "UPDATE classes SET fees = %s WHERE id = %s"

        try:
            cursor.execute(fees_query , (new_fees , cls_id))
            cursor.close()
            self.connection.commit()

            self.logger.event(location = LOCATION ,content = f"change class fees of class id {cls_id} to {new_fees}")
            return True
        except mysql.Error as ex:
            cursor.close()
            self.logger.error(location = LOCATION , content = f"error occur when change class fess of class id {cls_id} to {new_fees}", mysql_error = ex)

            return False

    def changeClassDescription(self, cls_id : int , new_description : str) -> bool:

        if not self.isClassExist(cls_id):
            self.logger.warning(location = LOCATION , content = f"try to change class description of invalid class with id : {cls_id}")
            return False

        cursor = self.connection.cursor()
        des_query = "UPDATE classes SET description = %s WHERE id = %s"

        try:
            cursor.execute(des_query, (new_description, cls_id))
            cursor.close()
            self.connection.commit()

            self.logger.event(location=LOCATION, content=f"change class description of class id {cls_id}")
            return True
        except mysql.Error as ex:
            cursor.close()
            self.logger.error(location=LOCATION,
                              content=f"error occur when change class description of class id {cls_id}",
                              mysql_error=ex)

            return False

    def changeClassName(self, cls_id : int , new_name : str) -> bool:

        if not self.isClassExist(cls_id):
            self.logger.warning(location = LOCATION , content = f"try to change class name of invalid class with id : {cls_id}")
            return False

        cursor = self.connection.cursor()
        name_query = "UPDATE classes SET class_name = %s WHERE id = %s"

        try:
            cursor.execute(name_query, (new_name, cls_id))
            cursor.close()
            self.connection.commit()

            self.logger.event(location=LOCATION, content=f"change class name of class id {cls_id}")
            return True
        except mysql.Error as ex:
            cursor.close()
            self.logger.error(location=LOCATION,
                              content=f"error occur when change class name of class id {cls_id}",
                              mysql_error=ex)

            return False

    def addTimes(self, cls_id : int, day_of_week : int , start_time : datetime.time,  end_time : datetime.time) -> bool:

        if day_of_week > 7:
            self.logger.warning(location = LOCATION , content = f"used invalid day of week number : {day_of_week}")
            return False

        # check of class is exists
        if not self.isClassExist(cls_id):
            self.logger.warning(location = LOCATION , content = f"used wrong class index  : {cls_id}")
            return False

        if start_time >= end_time:
            self.logger.warning(location = LOCATION , content = f"invalid times used for class : {start_time} to {end_time}")
            return False

        # check if time crashes other class times
        for time_item in self.getClassTimes():
            time_item["start_time"] = datetime.time.fromisoformat(str(time_item["start_time"]))
            time_item["end_time"] = datetime.time.fromisoformat(str(time_item["end_time"]))

            if time_item["day_of_week"] == day_of_week and DateTimeUtil.isCrash(time_item["start_time"], time_item["end_time"],
                                                                                start_time ,end_time):
                self.logger.warning(location = LOCATION , content = f"the times that used here are crash other times of other classes: {start_time} to {end_time}")
                return False

        cursor = self.connection.cursor()
        time_add_query = "INSERT INTO class_times(class_id, day_of_week, start_time ,end_time) VALUES (%s, %s, %s, %s)"

        cursor.execute(time_add_query , params=(cls_id , day_of_week ,start_time.strftime("%H:%M:%S"), end_time.strftime("%H:%M:%S")))
        cursor.close()
        self.connection.commit()

        # log the event
        self.logger.event(location = LOCATION , content = f"add new times to class under class id {cls_id}", day_of_week = day_of_week, start_time = str(start_time) , end_time = str(end_time))

        return True

    def swithTimes(self) -> bool:
        pass

    def initiateClassInstance(self, cls_id : int, student_list : list[int] , year : int = datetime.datetime.now().year) -> int:

        cursor = self.connection.cursor()
        instance_query = """INSERT INTO class_instance(class_id , year, students, started_at, initial_count, current_count)
                                    VALUES (%s, %s, %s, %s, %s, %s)"""

        try:
            cursor.execute(instance_query, (
                cls_id, year, json5.dumps(student_list), datetime.datetime.now().date(), len(student_list), len(student_list)
            ))
            ins_id = cursor.lastrowid

            cursor.close()
            self.connection.commit()

            self.logger.event(location = LOCATION, content = f"start new class instance of class id {cls_id}", instance_id = ins_id, student_count = len(student_list), year=year)
            return ins_id

        except mysql.Error as ex:
            cursor.close()

            self.logger.error(location = LOCATION, content = f"start class instance under class id {cls_id} is failed")
            return -1

    def addStudents(self, cls_ins_id : int , student_list : list[int]) -> int:

        # first get student list from the class instance table
        cursor = self.connection.cursor(dictionary=True)
        select_query = "SELECT students FROM class_instance WHERE id = %s  AND finished = %s LIMIT 1"

        cursor.execute(select_query, (cls_ins_id, False))
        std_list = cursor.fetchall()
        if std_list:
            current_student_ids = json5.loads(std_list[0].get("students"))
            # now update thr student id list
            current_student_ids.extend(student_list)

            update_query = "UPDATE class_instance SET students = %s WHERE id = %s"

            try:
                cursor.execute(update_query, (json5.dumps(current_student_ids), cls_ins_id))
                cursor.close()
                self.connection.commit()

                self.logger.event(location = LOCATION , content = f"update students of class with instance id {cls_ins_id}", current_count = len(current_student_ids))
                return len(current_student_ids)
            except mysql.Error as ex:
                cursor.close()

                self.logger.error(location = LOCATION, content = f"update students of class instance id {cls_ins_id} failed", mysql_error = str(ex))
                return -1

        self.logger.warning(location = LOCATION, content = f"try to update students of invalid class instance id : {cls_ins_id}")
        return -1

    def finishInstance(self, cls_ins_id) -> bool :

        cursor = self.connection.cursor()
        finished_query = "UPDATE class_instance SET finished = %s , ended_at = %s WHERE id = %s"

        try:
            cursor.execute(finished_query, (True, datetime.datetime.now().date(), cls_ins_id))
            cursor.close()
            self.connection.commit()

            self.logger.event(location = LOCATION , content = f"finished the class with instance id {cls_ins_id}")
            return True
        except mysql.Error as ex:
            self.logger.error(location = LOCATION , content = f"finishing class with instance id {cls_ins_id} is failed")
            cursor.close()
            return False

    def finishClass(self, cls_id : int) -> bool:

        cursor = self.connection.cursor()
        query = "UPDATE classes SET available = %s WHERE id = %s"

        try:
            cursor.execute(query, (False, cls_id))
            cursor.close()
            self.connection.commit()

            self.logger.event(location = LOCATION, content = f"end the class with class ID {cls_id}")
            return True
        except mysql.Error as ex:
            cursor.close()
            self.logger.error(location = LOCATION , content = f"ended class with class ID {cls_id} is failed")

            return False

    def isClassExist(self , cls_id : int) -> bool:

        check_query = "SELECT id FROM classes WHERE id = %s"
        cursor = self.connection.cursor()

        cursor.execute(check_query, (cls_id, ))
        result = cursor.fetchone()

        cursor.close()
        return bool(result)








