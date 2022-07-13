import datetime

import mysql.connector as mysql
from util.logger import Logger

from util.manager.class_engine import STD_KEYS

LOCATION = "CLASS MANAGER"

LABELED_KEYS = {
    "id" : "Class ID",
    "class_name" : "Class Name",
    "subject" : "Subject",
    "grade" : "Grade",
    "payment_method" : "Method of Payment",
    "fees" : "Class Fees",
    "started_at" : "Started",
    "available" : "Current Status"

}

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def labelingKeys(result_dict : list[dict]) -> None:
    _result = []
    for item in result_dict:
        _rst = {}
        for key in item.keys():
            # rename the keys of student dictionary
            _rst[LABELED_KEYS[key]] = item.get(key)
        _result.append(_rst)
    result_dict = _result

def assignWeekDayNames(list : list[dict]) -> None:

    for item in list:
        if item.get("day_of_week"):
            item["day_of_week"] = WEEKDAY_NAMES[item["day_of_week"] - 1]


class ClassManager:
    def __init__(self, connection : mysql.MySQLConnection , logger : Logger):
        self.connection = connection
        self.logger = logger

    @staticmethod
    def getKey(text: str):
        for key in STD_KEYS.keys():
            if (text.lower() in STD_KEYS.get(key)):
                return key

        return None

    def fetchClassWithKeys(self, search_query : str , labeled : bool = False , params : tuple = None , limit : int = None) -> list[dict]:

        # create a cursor instance
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(search_query , params=params)

        if limit:
            result = cursor.fetchmany(limit)
        else:
            result = cursor.fetchall()

        self.logger.info(location=LOCATION, content=f"searching for classes", result_count = cursor.rowcount)
        # reset the cursor and close
        cursor.reset()
        cursor.close()


        if labeled:
           self.labelingKeys(result)
        return result

    def getClasses(self, labeled = False, limit : int = None ,status = None):

        search_query = "SELECT * FROM classes"
        if status is not None:
            search_query += " WHERE available = %s"
            return self.fetchClassWithKeys(search_query, params=(status , ), limit=limit, labeled=labeled)
        return self.fetchClassWithKeys(search_query , labeled=labeled, limit=limit)

    def getClassWithID(self , cls_id : int, labeled : bool = False) -> dict:

        search_query = "SELECT * FROM classes WHERE id = %s LIMIT 1"
        result = self.fetchClassWithKeys(search_query, labeled=labeled ,params=(cls_id, ))

        if result:
            return result[0]
        return None

    def getClassesWithGrades(self, grade : int , labeled = False , limit : int =  None , status = None) -> list[dict]:

        search_query = "SELECT * FROM classes WHERE grade = %s"
        if status is not None:
            search_query += " AND available = %s"
            return self.fetchClassWithKeys(search_query , labeled=labeled , params=(grade, status), limit=limit)
        return self.fetchClassWithKeys(search_query, labeled=labeled, params=(grade, ), limit=limit)

    def getClassesBySubject(self, subject : str , labeled = False , limit : int = None, status = None) -> list[dict]:

        search_query = "SELECT * FROM classes WHERE subject = %s"
        if status is not None:
            search_query += " AND available = %s"
            return self.fetchClassWithKeys(search_query , params=(subject, status), labeled=labeled , limit=limit)
        return self.fetchClassWithKeys(search_query, labeled=labeled , params=(subject, status), limit = limit)

    def searchClassByName(self, name : str ,labeled = False , limit : int = None, status = None) -> list[dict]:

        search_query = "SELECT * FROM classes WHERE class_name LIKE '%{}%' ".format(name)
        if status is not None:
            search_query += " AND available = %s"
            return self.fetchClassWithKeys(search_query , params=(status, ) ,labeled=labeled , limit = limit)
        return self.fetchClassWithKeys(search_query, labeled=labeled , limit=limit)

    def getClassNames(self) -> list[str]:

        query = "SELECT class_name FROM classes ORDER class_name"
        cursor = self.connection.cursor()

        cursor.execute(query)

        # logging and return the result
        self.logger.info(location = LOCATION , content = "fetch class names", result_count = cursor.rowcount)
        return [item[0] for item in cursor.fetchall()]

    def getTimesByClassId(self, cls_id : int, labeled = False) -> list[dict]:

        query = "SELECT day_of_week , start_time , end_time FROM class_times WHERE class_id = %s ORDER BY day_of_week"
        cursor = self.connection.cursor(dictionary=True)

        cursor.execute(query , (cls_id, ))
        result = cursor.fetchall()

        self.logger.info(location = LOCATION , content = f"fetch class times under class ID {cls_id}", result_count = cursor.rowcount)

        cursor.close()
        # return the formatted data
        if labeled:
            assignWeekDayNames(result)
            labelingKeys(result)
        return result

    def getClassWithDayOfWeek(self, day_of_week : int, labeled = False) -> list[dict]:

        query = """SELECT cls.id , class_name, description, grade, subject, payment_method,
                            fees, start_time, end_time
                    FROM class_times AS ct
                    INNER JOIN classes as cls ON cls.id = ct.class_id 
                    WHERE ct.day_of_week = %s """
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, (day_of_week, ))

        result = cursor.fetchall()
        self.logger.info(location = LOCATION, content = f"fetch class times of day {day_of_week}", result_count = cursor.rowcount)

        if labeled:
            assignWeekDayNames(result)
            labelingKeys(result)
        return result


