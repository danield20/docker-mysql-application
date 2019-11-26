import pymysql
import time
import sys

db = None

def connect_to_database():
    global db

    # Open database connection
    db = pymysql.connect(host = "mysql-dev", user = "root", password = "password", db = "flights")

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # execute SQL query using execute() method.
    cursor.execute("SELECT VERSION()")

    # Fetch a single row using fetchone() method.
    data = cursor.fetchone()
    print ("Database version : %s " % data)

def print_possible_commands():
    print("help - print this list")
    print("add flight_id, flight_origin, flight_departure, dep_day, dep_hour, duration, seats_number")
    print("cancel flight_id")
    print("print - prints current flights")
    print("exit - exits administration app")

def print_flights():
    cursor = db.cursor()
    cursor.execute("select * from flights_table")
    rows = cursor.fetchall()

    for row in rows:
        print(row)

    cursor.close()

def add_flight(cmd):
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

def cancel_flight(cmd):
    delete_flight_id = cmd.split(' ')[1]

    cursor = db.cursor()
    try:
        cursor.execute("delete from flights_table where id = " + delete_flight_id)
    except pymysql.err.MySQLError as e:
        print(e)

    db.commit()
    cursor.close()


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
        elif line.split(" ")[0] == "add":
            add_flight(line)
        elif line.split(" ")[0] == "cancel":
            cancel_flight(line)

def main():
    # wait until sql database fully loaded
    time.sleep(15)

    connect_to_database()

    get_commands()

    # disconnect from server
    db.commit()
    db.close()

if __name__ == "__main__":
    main()
