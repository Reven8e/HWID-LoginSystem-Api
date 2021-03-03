from flask import Flask, json, Response, jsonify
from pymongo import MongoClient, errors
from secrets import uri

cluster = MongoClient(uri, maxPoolSize=50)
DB = cluster["auth"]
USERS = DB["users"]


def find(user):
    user = USERS.find_one({"_id": {"$regex": f"^{user}"}})
    return user


app = Flask(__name__)
app.secret_key = "sup"


@app.route('/api/create/<string:admin_key>/<string:user>/<string:password>', methods=['POST', 'GET'])
def create(user, password, admin_key):
    if admin_key != app.secret_key:
        response = Response(
                response=json.dumps({"message": "Invalid access key!"}),
                status=401,
                mimetype='application/json'
            )
        return response
    try:
        USERS.insert_one({"_id": user, "password": password, "hwid": None})
        response = Response(
                response=json.dumps({"message": "Successfuly created", "user": {"user": user, "password": password, "hwid": None}}),
                status=201,
                mimetype='application/json'
            )
    except errors.DuplicateKeyError:
        response = Response(
                response=json.dumps({"message": "Username is already in use."}),
                status=400,
                mimetype='application/json'
            )
    return response


@app.route('/api/login/<string:user>/<string:password>', methods=['POST', 'GET'])
def login(user, password):
    usr= find(user)
    if usr is not None:
        passwd = usr["password"]
        if passwd == password:
            response = Response(
                    response=json.dumps({"message": "Successfuly logged in."}),
                    status=200,
                    mimetype='application/json'
                )
    else:
        response = Response(
                response=json.dumps({"message": "User or password are inccorect."}),
                status=401,
                mimetype='application/json'
            )
    
    return response




if __name__ == "__main__":
    app.run(debug=True)