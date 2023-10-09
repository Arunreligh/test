from flask import Flask, jsonify, request
from pymongo import MongoClient
from flask_cors import CORS 
from bson import ObjectId
import json
import jwt
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from functools import wraps


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
bcrypt = Bcrypt(app)
secret = "abcdefgh"

# mongo = MongoClient('localhost', 27017)
# db = mongo['arun'] #py_api is the name of the db
# mongodb_uri = "mongodb+srv://<username>:<password>@clustername.mongodb.net/dbname"
# mongodb_uri = "mongodb+srv://arundanabalan94:XBcQzxfcBKBEnTPp@cluster0.bawls55.mongodb.net/arun"
uri = "mongodb+srv://arundanabalan94:lXFJWoxS6hs60NQr@cluster0.bawls55.mongodb.net/?retryWrites=true&w=majority"
mongo = MongoClient(uri)
db = mongo['arun'] 

@app.route('/', methods=['GET'])
def emety():
    return f'Serevr is running'
@app.route('/register', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        check = db['register'].find_one({"email": data['email']})
        if check:
            return jsonify({'status': 'fail', 'message': 'User with that email exists'}), 400
        data['created'] = datetime.now()

        result = db['register'].insert_one(data)
        if result.acknowledged:
            return jsonify({'status': 'success', 'message': 'User created successfully'}), 201
        else:
            return jsonify({'status': 'fail', 'message': 'User creation failed'}), 500
    except Exception as errorr:
        return jsonify({'status': 'error', 'message': str(errorr)}), 500

@app.route('/loginn', methods=['POST'])
def login1():
    try:
        data = request.get_json()
        data['created'] = datetime.now()

        result = db['login'].insert_one(data)
        if result.acknowledged:
            return jsonify({'status': 'success', 'message': 'User created successfully'}), 201
        else:
            return jsonify({'status': 'fail', 'message': 'User creation failed'}), 500
    except Exception as errorr:
        return jsonify({'status': 'error', 'message': str(errorr)}), 500



@app.route('/register/<string:user_id>', methods=['GET'])
def get_users(user_id):
    try:
        user = db['register'].find_one({"_id": ObjectId(user_id)})
        if user:
            user['_id'] = str(user['_id'])
            return jsonify({'status': 'success', 'data': user, 'message': 'User retrieved successfully'}), 200
        else:
            return jsonify({'status': 'fail', 'message': 'User not found'}), 404
    except Exception as errorr:
        return jsonify({'status': 'error', 'message': str(errorr)}), 500


def tokenReq(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        
        if "Authorization" in request.headers:
            token = request.headers["Authorization"]
            try:
                
               
                payload = jwt.decode(token, secret, algorithms=["HS256"])
    
                print(payload,'sssssssssss')
            except Exception as errorr:
                return jsonify({"status": "fail", "message": str(errorr)}), 401
            return f(*args, **kwargs)
        else:
            return jsonify({"status": "fail", "message": "unauthorized"}), 401
    return decorated



@app.route('/login', methods=['POST'])
def login():
    message = ""
    res_data = {}
    code = 500
    status = "fail"
    try:
        data = request.get_json()
        user = db['register'].find_one({"email": f'{data["email"]}'})
        if user:
            user['_id'] = str(user['_id'])
            print(user['password'],'$$$$$$$$$$$$$$')

            if user['password']:
                time = datetime.utcnow() + timedelta(hours=24)
                token = jwt.encode({
                        "user": {
                            "email": f"{user['email']}",
                            "id": f"{user['_id']}",
                        },
                        "exp": time
                    },secret)
                print(token,'#######')

                del user['password']

                message = f"user authenticated"
                code = 200
                status = "successful"
                res_data['token'] = token
                res_data['user'] = user

            else:
                message = "wrong password"
                code = 401
                status = "fail"
        else:
            message = "invalid login details"
            code = 401
            status = "fail"

    except Exception as errorr:
        message = f"{errorr}"
        code = 500
        status = "fail"
    return jsonify({'status': status, "data": res_data, "message":message}), code




@app.route('/templates', methods=['GET'])
@tokenReq  
def all_templates():
    try:
        templates = list(db['templates'].find({}, {"_id": 1, "template_name": 1, "subject": 1}))  
       
        for template in templates:
            template['_id'] = str(template['_id'])
        return jsonify({'status': 'success', 'data': templates, 'message': 'Templates retrieved successfully'}), 200
    except Exception as errorr:
        return jsonify({'status': 'error', 'message': str(errorr)}), 500


@app.route('/templates/<string:template_id>', methods=['GET'])
@tokenReq
def get_single_template(template_id):
    try:
        template = db['templates'].find_one({"_id": ObjectId(template_id)})
        if template:
            
            template['_id'] = str(template['_id'])
            return jsonify({'status': 'success', 'data': template, 'message': 'Template retrieved successfully'}), 200
        else:
            return jsonify({'status': 'fail', 'message': 'Template not found'}), 404
    except Exception as errorrr:
        return jsonify({'status': 'error', 'message': str(errorrr)}), 500


@app.route('/templates/<string:template_id>', methods=['PUT'])
@tokenReq
def update_single_template(template_id):
    try:
        data = request.get_json()
        
        result = db['templates'].update_one({"_id": ObjectId(template_id)}, {"$set": data})
        if result.modified_count > 0:
            return jsonify({'status': 'success', 'message': 'Template updated successfully'}), 200
        else:
            return jsonify({'status': 'fail', 'message': 'Template not found or not updated'}), 404
    except Exception as errorr:
        return jsonify({'status': 'error', 'message': str(errorr)}), 500
    
@app.route('/templates', methods=['POST'])
@tokenReq
def create_template():
    try:
        data = request.get_json()
        result = db['templates'].insert_one(data)
        if result.acknowledged:
            return jsonify({'status': 'success', 'message': 'Template created successfully', '_id': str(result.inserted_id)}), 201
        else:
            return jsonify({'status': 'fail', 'message': 'Template creation failed'}), 500
    except Exception as errorr:
        return jsonify({'status': 'error', 'message': str(errorr)}), 500


@app.route('/templates/<string:template_id>', methods=['DELETE'])
@tokenReq
def delete_single_template(template_id):
    try:
        
        result = db['templates'].delete_one({"_id": ObjectId(template_id)})
        if result.deleted_count > 0:
            return jsonify({'status': 'success', 'message': 'Template deleted successfully'}), 200
        else:
            return jsonify({'status': 'fail', 'message': 'Template not found or not deleted'}), 404
    except Exception as errorr:
        return jsonify({'status': 'error', 'message': str(errorr)}), 500


if __name__ == '__main__':
    # app.run(debug=True, host='0.0.0.0', port='5000')
    app.run()
