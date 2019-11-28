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
    return jsonify(rows)

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
    print(number_of_people)

    for flight_id in flight_list:
        print(flight_id)
        if not valid_flight(flight_id, number_of_people):
            return Response("Flight no longer available or capacity exceided", status=403)

    connect_to_database()
    cursor = db.cursor()

    cursor.execute("select res_id from reservations_table order by res_id desc limit 1")
    row = cursor.fetchone()
    if row == None:
        next_id = 1
    else:
        next_id = row[0] + 1

    values_to_add = "({}, {})".format(next_id, number_of_people)
    cursor.execute("insert into reservations_table values " + values_to_add)

    for flight_id in flight_list:
        values_to_add = "({}, {})".format(next_id, flight_id)
        cursor.execute("insert into reservations_flights values " + values_to_add)
        cursor.execute("update flights_table set seats_taken = seats_taken + " + str(number_of_people) + " where"\
            " id = " + str(flight_id))

    cursor.close()
    db.commit()
    db.close()

    return Response("Flights booked succesfully", status=201)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)