import os , json5
import mysql.connector as mysql

from util.security.access import AccessManager
from util.logger import Logger


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # create global instance of connection and loggers
    global connection, logger
    connection = mysql.connect()

