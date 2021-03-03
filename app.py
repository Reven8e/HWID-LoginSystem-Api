# © HWID Login System API- Made by Yuval Simon. For bogan.cool

from flask import Flask, json, Response, jsonify
from pymongo import MongoClient, errors
from secrets import uri

cluster = MongoClient(uri, maxPoolSize=50)
DB = cluster["auth"]
USERS = DB["users"]


def find(user):
    user = USERS.find_one({"_id": {"$regex": f"^{user}"}})
    print(user)
    return user


app = Flask(__name__)
app.secret_key = "sup"


@app.route('/api/register/<string:admin_key>/<string:user>/<string:password>', methods=['POST', 'GET'])
def create(user, password, admin_key):
    if admin_key != app.secret_key:
        response = Response(
                response=json.dumps({"status code": 401, "message": "Invalid access key!"}),
                status=401,
                mimetype='application/json')
        return response
    try:
        USERS.insert_one({"_id": user, "password": password, "hwid": None})
        response = Response(
                response=json.dumps({"status code": 201, "message": "Successfuly created", "user": {"user": user, "password": password, "hwid": None}}),
                status=201,
                mimetype='application/json')
    except errors.DuplicateKeyError:
        response = Response(
                response=json.dumps({"status code": 400, "message": "Username is already in use."}),
                status=400,
                mimetype='application/json')
    return response


@app.route('/api/login/<string:user>/<string:password>/<string:hwid>', methods=['POST', 'GET'])
def login(user, password, hwid):
    usr= find(user)
    if usr is not None:
        passwd = usr["password"]
        hwid_db = usr["hwid"]

        if passwd == str(password):
            if hwid_db is None:
                after = {"$set": {"hwid": str(hwid)}}
                USERS.update_one(usr, after)
                hwid_db = hwid

            if hwid_db == str(hwid):
                response = Response(
                        response=json.dumps({"status code": 200, "message": "Successfuly logged in."}),
                        status=200,
                        mimetype='application/json')
                return response

    response = Response(
            response=json.dumps({"status code": 401, "message": "User or password or hwid are inccorect."}),
            status=401,
            mimetype='application/json')

    return response


@app.route('/api/change-hwid/<string:admin_key>/<string:user>/<string:password>/<string:new_hwid>', methods=['PUT', 'GET'])
def change_hwid(admin_key, user, password, new_hwid):
    if admin_key != app.secret_key:
        response = Response(
                response=json.dumps({"status code": 401, "message": "Invalid access key!"}),
                status=401,
                mimetype='application/json')
        return response

    usr = find(user)
    if usr is not None:
        passwd = usr["password"]

        if passwd == str(password):
            after = {"$set": {"hwid": str(new_hwid)}}
            USERS.update_one(usr, after)
            response = Response(
                    response=json.dumps({"status code": 201, "message": "HWID has been successfuly updated."}),
                    status=201,
                    mimetype='application/json')
            return response

    response = Response(
            response=json.dumps({"status code": 401, "message": "User or password are inccorect."}),
            status=401,
            mimetype='application/json')

    return response


if __name__ == "__main__":
    app.run(debug=True)