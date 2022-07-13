# from test.test1 import name

global name
name = ""

class Test:
    def __init__(self, arg):
        global name
        name = arg
        print(name)

    def print(self):
        print(name)
