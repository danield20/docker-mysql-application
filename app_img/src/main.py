import pymysql
import time
import sys

db = None

def connect_to_database():
    global db

    # Open database connection
    while True:
        try:
            db = pymysql.connect(host = "mysql-dev", user = "root", password = "password", db = "flights")
            break
        except:
            continue

def print_possible_commands():
    print("help - print this list")
    print("add flight_id, flight_origin, flight_departure, dep_day, dep_hour, duration, seats_number")
    print("cancel flight_id")
    print("print - prints current flights")
    print("reservations - prints all current reservations")
    print("exit - exits administration app")

def print_flights():
    connect_to_database()
    cursor = db.cursor()
    cursor.execute("select * from flights_table")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()
    db.close()

def print_reservations():
    connect_to_database()
    cursor = db.cursor()
    cursor.execute("select * from reservations_table")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()
    db.close()

def add_flight(cmd):
    connect_to_database()
    flight_columns = cmd.split(' ')
    values_to_add = "({}, \"{}\", \"{}\", {}, {}, {}, {})".format(flight_columns[1],
                                                                  flight_columns[2],
                                                                  flight_columns[3],
                                                                  flight_columns[4],
                                                                  flight_columns[5],
                                                                  flight_columns[6],
                                                                  flight_columns[7])
    cursor = db.cursor()
    try:
        cursor.execute("insert into flights_table values " + values_to_add)
    except pymysql.err.MySQLError as e:
        print(e)

    db.commit()
    cursor.close()
    db.close()

def cancel_flight(cmd):
    connect_to_database()
    delete_flight_id = cmd.split(' ')[1]

    cursor = db.cursor()
    try:
        cursor.execute("delete from flights_table where id = " + delete_flight_id)
    except pymysql.err.MySQLError as e:
        print(e)

    db.commit()
    cursor.close()
    db.close()


def get_commands():
    print_possible_commands()

    while True:
        line = input("$- ")

        if line == "help":
            print_possible_commands()
        elif line == "exit":
            break
        elif line == "print":
            print_flights()
        elif line == "reservations":
            print_reservations()
        elif line.split(" ")[0] == "add":
            add_flight(line)
        elif line.split(" ")[0] == "cancel":
            cancel_flight(line)

if __name__ == "__main__":
    get_commands()
