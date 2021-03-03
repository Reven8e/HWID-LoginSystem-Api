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


def response(code: int, message: str):
    response = Response(
            response=json.dumps({"status code": code, "message": message}),
            status=code,
            mimetype='application/json')
    return response  


app = Flask(__name__)
app.secret_key = "knfcadrqif"


@app.route('/api/register/<string:admin_key>/<string:user>/<string:password>', methods=['POST', 'GET'])
def create(user, password, admin_key):
    if admin_key != app.secret_key:
        resp = response(401, "Invalid access key!")
        return resp

    try:
        USERS.insert_one({"_id": user, "password": password, "hwid": None})
        resp = Response(
                response=json.dumps({"status code": 201, "message": "Successfuly created", "user": {"user": user, "password": password, "hwid": None}}),
                status=201,
                mimetype='application/json')
    except errors.DuplicateKeyError:
        resp = response(400, "Username is already in use.")

    return resp


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
                resp = response(200, "Successfuly logged in.")
                return resp

    resp = response(401, "Username or password or hwid are inccorect!")
    return resp


@app.route('/api/change-hwid/<string:admin_key>/<string:user>/<string:password>/<string:new_hwid>', methods=['PUT', 'GET'])
def change_hwid(admin_key, user, password, new_hwid):
    if admin_key != app.secret_key:
        resp = response(401, "Invalid access key!")
        return resp

    usr = find(user)
    if usr is not None:
        passwd = usr["password"]

        if passwd == str(password):
            after = {"$set": {"hwid": str(new_hwid)}}
            USERS.update_one(usr, after)
            resp = response(201, "HWID has been successfuly updated.")
            return resp

    resp = response(400, "User or password are inccorect.")
    return resp


@app.route('/api/change-hwid/<string:admin_key>/<string:user>', methods=['DELETE', 'GET'])
def delete_user(admin_key, user):
    if admin_key != app.secret_key:
        resp = response(401, "Invalid access key!")
        return resp

    usr = find(user)
    if usr is not None:
        USERS.delete_one(usr)
        resp = response(201, f"Successfuly deleted {user}")
        return resp

    resp = response(400, f"{user} is not found!")
    return resp
    
    

if __name__ == "__main__":
    app.run(debug=True)