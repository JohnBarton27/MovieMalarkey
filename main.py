from flask import Flask, make_response, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit

from movie import Movie
from room import Room
from user import User

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app)
rooms = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/roomSearch', methods=['POST'])
def new_user():
    user = User(request.args.get('nickname'))
    resp = make_response(render_template('roomSearch.html', user=user))
    resp.set_cookie('user_name', user.name)
    return resp


@app.route('/newRoom', methods=['POST'])
def new_room():
    user = User(request.cookies.get('user_name'))
    room = Room(user)
    rooms.append(room)

    resp = make_response(room.code)
    resp.set_cookie('room', room.code)
    return resp


@app.route('/checkRoomCode')
def check_room_code():
    room_code = request.args.get('code')
    for room in rooms:
        if room.code == room_code:
            resp = make_response('true')
            resp.set_cookie('room', room.code)
            return resp

    return 'false'


@app.route('/startGame')
def start_game():
    # TODO add handling to make sure at least 3 people have joined the room
    room_code = request.args.get('code')
    for room in rooms:
        if room.code == room_code:
            room.start()
            resp = make_response(room.serialize())
            return resp

    return 'Room not found'


@app.route('/play')
def enter_room():
    user = User(request.cookies.get('user_name'))
    room_code = request.cookies.get('room')

    for room in rooms:
        if room.code == room_code:
            room.add_user(user)
            resp = make_response(render_template('room.html', room=room.serialize()))
            return resp

    return f'<h1>No room {room_code} found!</h1>'


@socketio.on('join_room')
def connect(data):
    user = User(request.cookies.get('user_name'))
    current_code = data['room']

    for open_room in rooms:
        if open_room.code == current_code:
            room = open_room
            join_room(room.code)
            send({'event': 'new-user', 'username': user.name, 'room': room.serialize()}, json=True, to=room.code)

            print(f'{user.name} joined {room.code}')
            break


@socketio.on('disconnect')
def disconnect():
    print('Disconnected!')


if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=8010, debug=True)
