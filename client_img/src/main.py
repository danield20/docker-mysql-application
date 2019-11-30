import requests
import time
import sys
import json

server_host = "myserver:5000"
adminapp_host = "myadmin-app:5000"
priviledged_mode = False

def print_possible_commands():
    print("\nNormal operations:")
    print("exit - exits client")
    print("help - print this list")
    print("login user passwd - enter priviledged mode")
    print("logout - log out of priviledged mode")
    print("print - prints current flights")
    print("optimal source dest max days")
    print("book flight_id nr_of_persons")
    print("buy res_id card_number\n")
    print("Privileged operations(require authentification):")
    print("add flight_id source destination day hour duration capacity")
    print("cancel flight_id")
    print("reservations - prints all current reservations")
    print("bought - see bought tickets\n")

# normal operation
def print_flights():
    url = "http://" + server_host + "/get_flights"
    r = requests.get(url)
    print(r.json())

def get_optimal(cmd):
    info = cmd.split(' ')
    PARAMS = {"source" : info[1],
              "dest"   : info[2],
              "max"    : info[3],
              "day"    : info[4]}
    url = "http://" + server_host + "/get_optimal"
    r = requests.get(url, params = PARAMS)
    if r.text.split(" ")[0] == "Sorry,":
        print(r.text)
    else:
        print(r.json())

def buy_ticket(cmd):
    info = cmd.split(' ')
    res_id = info[1]
    card_nr = info[2]

    PARAMS = {"res_id"   : res_id, "card_nr" : card_nr}
    url = "http://" + server_host + "/buy_ticket"
    r = requests.put(url, params = PARAMS)
    print(r.text)

def book_flights(cmd):
    info = cmd.split(' ')
    flights = []
    for i in range(1, len(info) - 1):
        flights.append(info[i])
    PARAMS = {"flight_id"   : json.dumps(flights), "nr" : info[len(info) - 1]}
    url = "http://" + server_host + "/book_flight"
    r = requests.put(url, params = PARAMS)
    print(r.text)

# privileged operation
def login(cmd):
    global priviledged_mode
    info = cmd.split(' ')
    user = info[1]
    passwd = info[2]
    PARAMS = {"username"   : user, "password" : passwd}
    url = "http://" + adminapp_host + "/login"
    r = requests.get(url, params= PARAMS)
    if r.text == "Login succesfull!":
        priviledged_mode = True
    print(r.text)

def print_reservations():
    url = "http://" + adminapp_host + "/get_reservations"
    r = requests.get(url)
    print(r.text)

def print_bought():
    url = "http://" + adminapp_host + "/get_bought"
    r = requests.get(url)
    print(r.text)

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
    global priviledged_mode
    print_possible_commands()

    while True:
        if priviledged_mode:
            line = input("admin$- ")
        else:
            line = input("$- ")

        if line == "help":
            print_possible_commands()
        elif line == "exit":
            break
        elif line == "print":
            print_flights()
        elif line == "logout":
            if priviledged_mode:
                priviledged_mode = False
                print("Logout succesfull!")
            else:
                print("You are not logged in!")
        elif line == "reservations":
            if priviledged_mode:
                print_reservations()
            else:
                print("You don't have permissions!")
        elif line == "bought":
            if priviledged_mode:
                print_bought()
            else:
                print("You don't have permissions!")
        elif line.split(" ")[0] == "login":
            login(line)
        elif line.split(" ")[0] == "buy":
            buy_ticket(line)
        elif line.split(" ")[0] == "optimal":
            get_optimal(line)
        elif line.split(" ")[0] == "book":
            book_flights(line)
        elif line.split(" ")[0] == "add":
            if priviledged_mode:
                add_flight(line)
            else:
                print("You don't have permissions!")
        elif line.split(" ")[0] == "cancel":
            if priviledged_mode:
                cancel_flight(line)
            else:
                print("You don't have permissions!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        server_host = sys.argv[1] + ":8002"
        adminapp_host = sys.argv[1] + ":8001"
    get_commands()
