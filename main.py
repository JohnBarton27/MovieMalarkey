from flask import Flask, make_response, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send

from movie import Movie
from room import Room
from user import User

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/roomSearch', methods=['POST'])
def new_user():
    form_data = request.form
    user = User(form_data['Nickname'])
    resp = make_response(render_template('roomSearch.html', user=user))
    resp.set_cookie('user_name', user.name)
    return resp


@app.route('/newRoom', methods=['POST'])
def new_room():
    user = User(request.cookies.get('user_name'))
    room = Room.new_room(user)

    resp = make_response(render_template('room.html', room=room))
    resp.set_cookie('room', room.code)
    return resp


@app.route('/joinRoom', methods=['POST'])
def join_malarkey_room():
    user = User(request.cookies.get('user_name'))
    form_data = request.form
    room_code = form_data['Room_Code']

    room = Room.get_room(room_code)
    if room is not None:
        room.add_user(user)
        resp = make_response(render_template('room.html', room=room))
        resp.set_cookie('room', room.code)

        return resp           
    return f'<h1>No room {room_code} found!</h1>'


@socketio.on('join')
def connect(data):
    user = User(request.cookies.get('user_name'))
    room = Room.get_room(request.cookies.get('room'))
    
    if room is not None:
        print(f'{user.name} joined {room.code}')


@socketio.on('disconnect')
def disconnect():
    print('Disconnected!')


if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=8010, debug=True)
