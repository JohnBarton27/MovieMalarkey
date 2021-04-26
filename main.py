from flask import Flask, make_response, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from urllib.parse import unquote

from movie import Movie
from room import Room
from user import User

app = Flask(__name__, template_folder='templates')
socketio = SocketIO(app)
rooms = []
users = []


def _get_user(username):
    for user in users:
        if user.name == username:
            return user


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


@app.route('/submitGuess', methods=['POST'])
def submit_guess():
    data = unquote(str(request.data))
    guess = data.split('=')[-1]
    user = _get_user(request.cookies.get('user_name'))
    user.current_answer = guess
    return 'Success'


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

            socketio.send({'event': 'start-game', 'room': room.serialize()}, json=True, to=room.code)

            # Start the first round
            start_round()

            return resp

    return 'Room not found'


@app.route('/startRound')
def start_round():
    room_code = request.args.get('code')
    for room in rooms:
        if room.code == room_code:
            # Found the room
            movie = Movie.get_random()
            room.current_movie = movie

            # Send title & plot to host
            socketio.send({'event': 'movie', 'title': movie.title, 'plot': movie.plot}, json=True, to=room.current_judge.socket_client)

            # Send title to rest of users
            for guesser in room.users:
                if guesser == room.current_judge:
                    continue
                socketio.send({'event': 'movie-title', 'title': movie.title}, json=True,
                              to=guesser.socket_client)

            return 'Started round!'

    return 'Room not found'


@app.route('/play')
def enter_room():
    room_code = request.cookies.get('room')

    for room in rooms:
        if room.code == room_code:
            resp = make_response(render_template('room.html', room=room.serialize()))
            return resp

    return f'<h1>No room {room_code} found!</h1>'


@socketio.on('join_room')
def connect(data):
    user = User(request.cookies.get('user_name'))
    user.socket_client = request.sid
    current_code = data['room']

    for open_room in rooms:
        if open_room.code == current_code:
            open_room.add_user(user)

            users.append(user)

            room = open_room
            join_room(room.code)

            # TODO remove 'plot' from movies if not sending to judge
            send({'event': 'new-user', 'username': user.name, 'room': room.serialize()}, json=True, to=room.code)

            print(f'{user.name} joined {room.code} ({user.socket_client})')
            break


@socketio.on('disconnect')
def disconnect():
    print('Disconnected!')


if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=8010, debug=True)
