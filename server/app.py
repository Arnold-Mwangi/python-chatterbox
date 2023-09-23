from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)
@app.route('/')
def index():
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
    return response
if __name__ == '__main__':
    app.run(port=5555)
