import requests
import time
import sys
import json

server_host = "myserver:5000"
adminapp_host = "myadmin-app:5000"

def print_possible_commands():
    print("help - print this list")
    print("add flight_id flight_origin flight_departure dep_day dep_hour duration seats_number")
    print("cancel flight_id")
    print("book flight_id nr_of_persons")
    print("print - prints current flights")
    print("reservations - prints all current reservations")
    print("exit - exits administration app")

# normal operation
def print_flights():
    url = "http://" + server_host + "/get_flights"
    r = requests.get(url)
    print(r.json())

def book_flight(cmd):
    info = cmd.split(' ')
    flights = []
    for i in range(1, len(info) - 1):
        flights.append(info[i])
    PARAMS = {"flight_id"   : json.dumps(flights), "nr" : info[len(info) - 1]}
    url = "http://" + server_host + "/book_flight"
    r = requests.put(url, params = PARAMS)
    print(r.text)


# privileged operation
def print_reservations():
    url = "http://" + adminapp_host + "/get_reservations"
    r = requests.get(url)
    print(r.json())

# privileged operation
def add_flight(cmd):
    flight_columns = cmd.split(' ')
    PARAMS = {"flight_id"   : flight_columns[1],
              "source"      : flight_columns[2],
              "destination" : flight_columns[3],
              "depart_date" : flight_columns[4],
              "depart_hour" : flight_columns[5],
              "duration"    : flight_columns[6],
              "nr"          : flight_columns[7]}

    url = "http://" + adminapp_host + "/add_flight"
    r = requests.put(url, params = PARAMS)
    print(r.text)

# privileged operation
def cancel_flight(cmd):
    delete_flight_id = cmd.split(' ')[1]
    PARAMS = {"flight_id"   : delete_flight_id}
    url = "http://" + adminapp_host + "/cancel_flight"
    r = requests.put(url, params = PARAMS)
    print(r.text)


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
        elif line.split(" ")[0] == "book":
            book_flight(line)
        elif line.split(" ")[0] == "add":
            add_flight(line)
        elif line.split(" ")[0] == "cancel":
            cancel_flight(line)

if __name__ == "__main__":
    get_commands()
