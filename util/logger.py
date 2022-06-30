import json5, os
import datetime as dt
import mysql.connector as mysql

from util.security.access import AccessManager

class Logger:

    BUFFER_MAX_SIZE = 10
    LOG_PATH = "log"

    LEVELS = {
        "warnings.log" : "WARNING",
        "info.log" : "INFO",
        "debug.log" : "DEBUG",
        "error.log" : "ERROR"
    }

    def __init__(self, connection, *args, **kwargs) -> None:
        self.connection : mysql.MySQLConnection = connection
        # initiate the log buffer for each of log types
        self.warning_buffer = list()
        self.error_buffer = list()
        self.debug_buffer = list()
        self.info_buffer = list()

        self.log_links = {
            "warnings.log" : self.warning_buffer,
            "info.log" : self.info_buffer,
            "debug.log" : self.debug_buffer,
            "error.log" : self.error_buffer
        }

        # special log buffer for events/activity
        self.events = []


    def setConnection(self, connection : mysql.MySQLConnection) -> None:

        self.connection = connection

    def setAccessManager(self, access_manager : AccessManager):

        self.access_manager = access_manager

    def flushBuffer(self, file_name : str, buffer : list) -> None:

        with open(os.path.join(self.LOG_PATH, file_name), mode="r") as file:
            data = json5.load(file)

        if data is not None:
            data = [*data, *buffer]
        else:
            data = buffer

        with open(os.path.join(self.LOG_PATH, file_name), mode="r") as file:
            json5.dump(data, file, indent=4)

        # clear the buffers
        buffer.clear()

    def flush(self):

        # empty the all cache log memory and pass to the log files
        for file_name, buffer in self.log_links.items():
            self.flushBuffer(file_name, buffer)

    def attachTimeStamp(self, data_dict : dict):

        data_dict["timestamp"] = dt.datetime.now()

    def warning(self, **kwargs):

        self.attachTimeStamp(kwargs)

        if len(self.warning_buffer) >= self.BUFFER_MAX_SIZE:
            self.flushBuffer("warnings.log", self.warning_buffer)

        self.warning_buffer.append(kwargs)

    def info(self, **kwargs):

        self.attachTimeStamp(kwargs)

        if len(self.info_buffer) >= self.BUFFER_MAX_SIZE:
            self.flushBuffer("info.log", self.info_buffer)

        self.info_buffer.append(kwargs)

    def error(self, **kwargs):

        self.attachTimeStamp(kwargs)

        if len(self.error_buffer) >= self.BUFFER_MAX_SIZE:
            self.flushBuffer("error.log", self.error_buffer)

        self.error_buffer.append(kwargs)

    def debug(self, **kwargs):

        self.attachTimeStamp(kwargs)

        if len(self.debug_buffer) >= self.BUFFER_MAX_SIZE:
            self.flushBuffer("debug.log", self.debug_buffer)

        self.debug_buffer.append(kwargs)

    def flushEvents(self) -> None:

        with open(os.path.join(self.LOG_PATH, "event.json"), mode="r") as file:
            data = json5.load(file)

        if data is not None:
            data = [*data , self.events]
        else:
            data = self.events

        with open(os.path.join(self.LOG_PATH, "event.json"), mode="w") as file:
            json5.dump(data, file, indent=2)

        # clear the event buffer
        self.events.clear()


    def passEventsToServer(self, session_id : int):

        with open(os.path.join(self.LOG_PATH, "event.json"), mode="r") as file:
            events = json5.load(file)
            # clear the event log file
        with open(os.path.join(self.LOG_PATH, "event.json"), mode="w") as file:
            pass

        # flush the events buffer and save to the database
        cursor = self.connection.cursor()
        event_data = []
        for event in events:
            event_data.append(
                [
                    session_id,
                    event["timestamp"],
                    json5.dumps(event)
                ]
            )

        event_save_query = "INSERT INTO events(session_id, time, content) VALUES (%d, %s, %s)"
        cursor.executemany(event_save_query, event_data)

        self.connection.commit()
        cursor.close()


    def event(self, **kwargs):

        self.attachTimeStamp(kwargs)

        if len(self.events) >= self.BUFFER_MAX_SIZE:
            self.flushEvents()

        self.events.append(kwargs)

    def freeUpCache(self, session_id : int) -> None:

        cursor = self.connection.cursor()
        log_insert_query = "INSERT INTO logs(session_id , level, content) VALUES(%d, %s, %s)"
        # free the cache log files and pass to the server database
        for file_name in self.log_links.keys():
            with open(os.path.join(self.LOG_PATH, file_name) , mode="rw") as file:
                data = file.read()
                file.write("")

                cursor.execute(log_insert_query,
                               [session_id, self.LEVELS.get(file_name), data])

        self.connection.commit()
        # close the cursor
        cursor.close()





