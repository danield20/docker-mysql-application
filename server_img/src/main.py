import pymysql
from flask import Flask, jsonify, request, Response

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
    cursor.execute("select number_seats from flights_table where id = " + flight_id)
    row = cursor.fetchone()
    if row == None:
        return False
    capacity = row[0]
    cursor.execute("select sum(number_persons) from reservations_table where flight_id = " + flight_id)
    row = cursor.fetchone()
    if row[0] != None:
        if row[0] > capacity*1.1:
            return False
    print(capacity, row[0], flush=True)
    return True


@app.route('/book_flight', methods=['PUT'])
def book_flight():
    args = request.args
    flight_id = args.get('flight_id')
    number_of_people = args.get('nr')

    if not valid_flight(flight_id, number_of_people):
        return Response("Flight no longer available or capacity exceided", status=403)

    connect_to_database()
    cursor = db.cursor()

    values_to_add = "(NULL, {}, {})".format(flight_id, number_of_people)
    cursor.execute("insert into reservations_table values " + values_to_add)

    cursor.close()
    db.commit()
    db.close()

    return Response("Bine sefu", status=201)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False)