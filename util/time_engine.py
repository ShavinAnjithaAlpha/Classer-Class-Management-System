from PyQt5.QtCore import QDate, QTime
from datetime import datetime, time, date

class DateTimeUtil:

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    months  = [QDate.shortMonthName(i) for i in range(1, 13)]

    @staticmethod
    def getWeekDay(dayOfWeek : int):
        if (dayOfWeek > 7):
            raise IndexError("Week Day cannot exceeds the 7")


        return DateTimeUtil.days_of_week[dayOfWeek - 1]

    # create the additional static method for utility
    @staticmethod
    def isCrash(ex_time1 : time, ex_time2 : time , new_time1 : time , new_time2 : time):
        min_time = min(ex_time1, ex_time2)
        max_time = max(ex_time1, ex_time2)

        new_min = min(new_time1, new_time2)
        new_max = max(new_time1, new_time2)

        if (new_max < max_time and new_max > min_time):
            return True
        if (new_min > min_time and new_min < max_time):
            return True

    @staticmethod
    def gradeFromDate(birthDay : datetime):

        today = date.today()
        # calculated age from date object's years
        age = today.year - birthDay.year

        grade : int  = age - 5
        if birthDay.month == 1:
            grade += 1

        return grade


