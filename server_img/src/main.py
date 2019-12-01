import pymysql
from flask import Flask, jsonify, request, Response
import json

app = Flask(__name__)
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

@app.route('/get_flights', methods=['GET'])
def get_flights():
    connect_to_database()
    cursor = db.cursor()
    cursor.execute("select * from flights_table")
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return_str = ""
    format_str = "Id: {:{width2}} | Origin: {:{width}} | Destination: {:{width}} | Departure day: {:{width2}} |" \
                  " Departure hour: {:{width2}} | Duration: {:{width2}} \n"
    for row in rows:
        return_str += format_str.format(row[0], row[1], row[2], row[3], row[4], row[5], width = 10, width2 = 3)

    return jsonify(return_str[:-1])

def add_neigh(node, row):
    neigh_list = node[1]
    time_already_spent = node[0][4]

    if row[4] + row[5] >= 24:
        arrival_day = row[3] + 1
        arrival_hour = (row[4] + row[5]) % 24
    else:
        arrival_day = row[3]
        arrival_hour = row[4] + row[5]

    if time_already_spent == 0:
        time_already_spent = row[5]
    else:
        time_already_spent += (arrival_day * 24 + arrival_hour) - (node[0][1] * 24 + node[0][2])

    neigh_list.append(((row[2], arrival_day, arrival_hour, row[0], time_already_spent), []))

def add_layer(node, is_not_root = True):
    current_city = node[0][0]
    current_day = node[0][1]
    current_hour = node[0][2]
    if current_hour + 1 >= 24:
        departure_hour = (current_hour + 1) % 24
        departure_day  = current_day + 1
    else:
        departure_hour = current_hour + 1
        departure_day = current_day

    all_possible_flights = []

    connect_to_database()
    cursor = db.cursor()

    # get flights in the same day
    cursor.execute("select * from flights_table where origin = \"" + current_city \
    + "\" and depart_date = " + str(departure_day) + " and depart_hour >= " + str(departure_hour))
    rows = cursor.fetchall()
    all_possible_flights.extend(rows)

    # if it is the first flight, we have to leave in the exact day
    if is_not_root:
        # get flights in the next days
        cursor.execute("select * from flights_table where origin = \"" + current_city \
        + "\" and depart_date > " + str(departure_day))
        rows = cursor.fetchall()
        all_possible_flights.extend(rows)

    for row in all_possible_flights:
        add_neigh(node, row)

    cursor.close()
    db.close()

def construct_graph(source, dest, max_flights, dep_day):
    root = ((source, dep_day, -1, -1, 0), [])
    current_level = [root]
    current_flight_number = 0
    while current_flight_number < int(max_flights):
        new_current_level = []
        for node in current_level:
            if node[0][0] == dest:
                continue
            if node[0][2] == -1:
                add_layer(node, is_not_root=False)
            else:
                add_layer(node)
            new_current_level.extend(node[1])
        current_level = new_current_level
        current_flight_number += 1
    return root

def print_graph(root, nrtabs):
    print("\t"*nrtabs,root[0], flush=True)
    for neigh in root[1]:
        print_graph(neigh, nrtabs+1)

def reconstruct_flights(final_flight, road):
    flights = [final_flight]
    cur_tuple = final_flight

    while road[cur_tuple] != None:
        prev_flight = road[cur_tuple]
        flights.append(prev_flight)
        cur_tuple = prev_flight

    flights.reverse()

    return flights

def get_best_route(root, dest):
    open = [root]
    act = {}
    act[root[0]] = None
    best_route = None
    best_time = 1000000000

    while open != []:
        current = open.pop(0)

        if current[0][0] == dest:
            if current[0][4] < best_time:
                best_time = current[0][4]
                best_route = reconstruct_flights(current[0], act)
        else:
            neighs = current[1]
            for neigh in neighs:
                if neigh[0][4] >= best_time:
                    continue
                act[neigh[0]] = current[0]
                open.insert(0, neigh)

    return best_route

def get_opt(source, dest, max_flight, dep_day):
    root = construct_graph(source, dest, max_flight, dep_day)
    #print_graph(root, 0)
    opt_route = get_best_route(root, dest)
    # print(opt_route, flush=True)
    return opt_route

def beautify_route(route):
    return_str = ""
    connect_to_database()
    cursor = db.cursor()
    string = "("
    for idx, id in enumerate(route):
        if idx == len(route) - 1:
            string += str(id)
        else:
            string += str(id) + ", "
    string += ")"
    cursor.execute("select * from flights_table where id in " + string)
    rows = cursor.fetchall()
    cursor.close()
    db.close()

    to_book_str = "To book give command: book "
    format_str = "Id: {:{width2}} | Origin: {:{width}} | Destination: {:{width}} | Departure day: {:{width2}} |" \
                  " Departure hour: {:{width2}} | Duration: {:{width2}} \n"

    for row in rows:
        return_str += format_str.format(row[0], row[1], row[2], row[3], row[4], row[5], width = 15, width2 = 3)
        to_book_str += str(row[0]) + " "
    to_book_str += "number_persons"

    return return_str + to_book_str

@app.route('/get_optimal', methods=['GET'])
def get_optimal():
    args = request.args
    try:
        source = args.get('source')
        dest = args.get('dest')
        max_flights = args.get('max')
        dep_day = args.get('day')
    except Exception as e:
        return "Error calculating optimal\n" + str(e)

    try:
        best_route = get_opt(source, dest, max_flights, dep_day)
    except pymysql.err.MySQLError as e:
        return "Error calculating optimal!\n" + str(e)

    if best_route == None or len(best_route) == 1:
        return "Sorry, no route available!"

    best_route_flight_ids = [x[3] for x in best_route]
    route_str = beautify_route(best_route_flight_ids)

    return jsonify(route_str)

def valid_flight(flight_id, nr):
    connect_to_database()
    cursor = db.cursor()
    cursor.execute("select capacity, seats_taken from flights_table where id = " + flight_id)
    row = cursor.fetchone()
    if row == None:
        return False
    capacity = row[0]
    seats_taken = row[1] + nr
    if seats_taken > capacity*1.1:
        return False

    return True

@app.route('/book_flight', methods=['PUT'])
def book_flight():
    args = request.args
    flight_list = json.loads(args.get('flight_id'))
    number_of_people = json.loads(args.get('nr'))

    for flight_id in flight_list:
        try:
            if not valid_flight(flight_id, number_of_people):
                return "Flight no longer available or capacity exceided!"
        except pymysql.err.MySQLError as e:
            return "Error booking flight!\n" + str(e)

    connect_to_database()
    cursor = db.cursor()

    try:
        cursor.execute("select res_id from reservations_table order by res_id desc limit 1")
    except pymysql.err.MySQLError as e:
        return "Error booking flight!\n" + str(e)

    row = cursor.fetchone()
    if row == None:
        next_id = 1
    else:
        next_id = row[0] + 1

    values_to_add = "({}, {})".format(next_id, number_of_people)

    try:
        cursor.execute("insert into reservations_table values " + values_to_add)
    except pymysql.err.MySQLError as e:
        return "Error booking flight!\n" + str(e)

    for flight_id in flight_list:
        values_to_add = "({}, {})".format(next_id, flight_id)
        try:
            cursor.execute("insert into reservations_flights values " + values_to_add)
            cursor.execute("update flights_table set seats_taken = seats_taken + " + str(number_of_people) + " where"\
                " id = " + str(flight_id))
        except pymysql.err.MySQLError as e:
            return "Error booking flight!\n" + str(e)

    cursor.close()
    db.commit()
    db.close()

    return "Flights booked succesfully, reservation id: " + str(next_id)

@app.route('/buy_ticket', methods=['PUT'])
def buy_ticket():
    args = request.args

    try:
        res_id = json.loads(args.get('res_id'))
        card_number = json.loads(args.get('card_nr'))
    except Exception as e:
        return "Error in parameters\n" + str(e)

    connect_to_database()
    cursor = db.cursor()

    try:
        cursor.execute("select * from reservations_table where res_id = " + str(res_id))
    except pymysql.err.MySQLError as e:
        return "Error buying ticket!\n" + str(e)

    row = cursor.fetchone()
    if row == None:
        return "Reservation is no longer available!"
    number_of_people = row[1]

    try:
        cursor.execute("select flight_id from reservations_flights where res_id = " + str(res_id))
    except pymysql.err.MySQLError as e:
        return "Error buying ticket!\n" + str(e)

    ids = cursor.fetchall()
    buy_string_flights = "("
    for id in ids:
        buy_string_flights += str(id[0]) + ","
    buy_string_flights = buy_string_flights[:-1]
    buy_string_flights += ")"

    try:
        cursor.execute("select * from flights_table where id in " + buy_string_flights)
    except pymysql.err.MySQLError as e:
        return "Error buying ticket!\n" + str(e)

    rows = cursor.fetchall()

    values_to_add = "({}, {}, {})".format("NULL", res_id, card_number)
    try:
        cursor.execute("insert into bought_tickets values " + values_to_add)
    except pymysql.err.MySQLError as e:
        return "Error buying ticket!\n" + str(e)

    cursor.close()
    db.commit()
    db.close()

    buy_string = ""
    flights_str = ""
    format_str = "Id: {:{width2}} | Origin: {:{width}} | Destination: {:{width}} | Departure day: {:{width2}} |" \
                  " Departure hour: {:{width2}} | Duration: {:{width2}} \n"
    for row in rows:
        flights_str += format_str.format(row[0], row[1], row[2], row[3], row[4], row[5], width = 10, width2 = 3)

    buy_string += "Bought ticket for reservation: " + str(res_id) + ", " + str(number_of_people) + " seats\n"
    buy_string += flights_str

    return buy_string[:-1]

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)