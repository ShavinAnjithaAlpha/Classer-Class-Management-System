import datetime

date1 = datetime.datetime.now()
date2 = datetime.datetime.now()

print((date2 - date1))
print(date2.strftime("%Y-%m-%d %H:%M:%S "))

print(date2.strftime("%A"))
print(date2)

d1 = datetime.datetime(year=2022, month=1, day=11)
d2 = datetime.datetime(year=2002, month=1, day=11)
print((d1.year - d2.year))