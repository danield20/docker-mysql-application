import pymysql
from flask import Flask, jsonify, request, Response
import time
import sys

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
def print_flights():
    connect_to_database()
    cursor = db.cursor()
    cursor.execute("select * from flights_table")
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(rows)

@app.route('/get_reservations', methods=['GET'])
def print_reservations():
    connect_to_database()
    cursor = db.cursor()
    cursor.execute("select * from reservations_table")
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(rows)

@app.route('/add_flight', methods=['PUT'])
def add_flight():
    args = request.args
    flight_id = args.get('flight_id')
    origin = args.get('source')
    destination = args.get('destination')
    depart_date = args.get('depart_date')
    depart_hour = args.get('depart_hour')
    duration = args.get('duration')
    number_of_people = args.get('nr')
    connect_to_database()
    values_to_add = "({}, \"{}\", \"{}\", {}, {}, {}, {}, {})".format(flight_id,
                                                                      origin,
                                                                      destination,
                                                                      depart_date,
                                                                      depart_hour,
                                                                      duration,
                                                                      number_of_people,
                                                                      0)
    cursor = db.cursor()
    try:
        cursor.execute("insert into flights_table values " + values_to_add)
    except pymysql.err.MySQLError:
        return "Error inserting flight"

    db.commit()
    cursor.close()
    db.close()
    return "Flight succesfully added"

@app.route('/cancel_flight', methods=['PUT'])
def cancel_flight():
    args = request.args
    flight_id = args.get('flight_id')
    connect_to_database()
    cursor = db.cursor()

    try:
        cursor.execute("select distinct(res_id) from reservations_flights where flight_id = " + flight_id)
    except pymysql.err.MySQLError:
        return "Error canceling flight"

    rows = cursor.fetchall()
    for row in rows:
        try:
            cursor.execute("delete from reservations_table where res_id = " + str(row[0]))
        except pymysql.err.MySQLError:
            return "Error canceling flight"

    try:
        cursor.execute("delete from flights_table where id = " + flight_id)
    except pymysql.err.MySQLError:
        return "Error canceling flight"

    db.commit()
    cursor.close()
    db.close()
    return "Flight succesfully canceled"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)
    # get_commands()
