from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
import json 
import os
from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

def export_data_to_frontend():
        messages = Message.query.all()
        messages_serialized = []

        for message in messages:
            message_data = {
                "id": message.id,
                "username": message.username,
                "body": message.body
            }
            
            # Check if updated_at is not None before formatting it
            if message.updated_at is not None:
                message_data["updated_at"] = message.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            
            # Check if created_at is not None before formatting it
            if message.created_at is not None:
                message_data["created_at"] = message.created_at.strftime('%Y-%m-%d %H:%M:%S')

            messages_serialized.append(message_data)

        # Wrap the messages in an object with a key
        data_to_export = {"messages": messages_serialized}

        # Construct the absolute path to the JSON file
        base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))  # Go up one directory
        json_file_path = os.path.join(base_dir, 'client', 'db.json')

        with open(json_file_path, 'w') as json_file:
            json.dump(data_to_export, json_file, indent=2) 


@app.route('/')
def index():
    export_data_to_frontend()
    return '<h3> We send Messages</h3>'



@app.route('/messages', methods=['GET', 'POST'])
def messages():

    messages =  Message.query.all()
    if request.method == 'GET':
        messages_serialized= [message.to_dict() for message in messages]

        response = make_response(
            messages_serialized,
            200
        )
        export_data_to_frontend()
        return response
        
    elif request.method == 'POST':
        data = request.json
        new_message = Message(
            body = data.get("body"),
            username = data.get("username"))
            
        db.session.add(new_message)
        db.session.commit()

        message_dict = new_message.to_dict()

        response = make_response(
            jsonify(message_dict),
            201
        )

        export_data_to_frontend()
        return response

@app.route('/messages/<int:id>', methods = ['PATCH', 'DELETE'])
def messages_by_id(id):

    message = Message.query.get(id)

    if request.method =='PATCH':
        data = request.json

        for attr, value in data.items():
            setattr(message, attr, value)

            db.session.add(message)
            db.session.commit()

            message_dict = message.to_dict()
            response = make_response(jsonify(message_dict),
            200)

        export_data_to_frontend()
        return response

    elif request.method =='DELETE':
        db.session.delete(message)
        db.session.commit()
        
        response_body = {
            "delete_status":"successful",
            "message":"message deleted"
        }

        response = make_response(
            jsonify(response_body),
            200
        )
    export_data_to_frontend()
    return response
if __name__ == '__main__':
    app.run(port=5555)
