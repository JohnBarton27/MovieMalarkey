from flask import Flask, make_response, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, send, emit
import os
from urllib.parse import unquote

from movie import Movie
from room import Room
from user import User

app = Flask(__name__, template_folder=os.path.abspath('../templates'))
socketio = SocketIO(app)
rooms = []
users = []


def _get_user(username):
    for user in users:
        if user.name == username:
            return user


def _get_user_from_room(username, room):
    for user in room.users:
        if user.name == username:
            return user


def _get_room(room_code):
    for room in rooms:
        if room.code == room_code:
            return room


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
    room = _get_room(request.cookies.get('room'))

    # Handle non-existent room
    if not room:
        return 'false'

    data = unquote(str(request.data))

    # Grab everything after '=' and strip off trailing single quote (')
    guess = data.split('=')[-1][:-1]
    user = _get_user_from_room(request.cookies.get('user_name'), room)
    user.current_answer = guess

    # Acknowledge submission to other users
    for guesser in room.users:
        socketio.send({'event': 'user-answered', 'room': room.serialize()}, json=True,
                      to=guesser.socket_client)

    # Send the host the guess
    socketio.send({'event': 'user-guess', 'room': room.serialize(full=True)}, json=True,
                  to=room.current_round.judge.socket_client)

    # All users have submitted
    if room.all_guesses_submitted:
        # Progress room to the VOTING phase
        room.open_voting()

        # Send non-full room to guessers
        for user in room.current_round.guessers:
            socketio.send({'event': 'all-guesses-submitted', 'room': room.serialize()}, json=True,
                          to=user.socket_client)

        # Send full room to judge
        socketio.send({'event': 'all-guesses-submitted', 'room': room.serialize(full=True)}, json=True,
                      to=room.current_round.judge.socket_client)

    return 'Success'


@app.route('/revealGuess', methods=['POST'])
def reveal_guess():
    room = _get_room(request.cookies.get('room'))
    user = _get_user_from_room(request.args.get('username'), room)

    answer_to_reveal = room.current_round.movie.plot if user == room.current_round.judge else user.current_answer
    print(f'Revealing "{answer_to_reveal}"...')
    socketio.send({'event': 'guess-reveal', 'plot': answer_to_reveal}, json=True, to=room.code)
    return "Success"


@app.route('/vote', methods=['POST'])
def vote():
    room = _get_room(request.cookies.get('room'))
    user = _get_user_from_room(request.cookies.get('user_name'), room)
    data = unquote(str(request.data))

    user.current_vote = data.split('=')[-1][:-1]

    if user.current_vote == room.current_round.movie.plot:
        # Correct Guess - voter gets 2 points
        room.current_round.give_points(2, user)
        pass
    else:
        # Incorrect Guess
        for guesser in room.current_round.guessers:
            if user.current_vote == guesser.current_answer and user != guesser:
                # 'guesser' gets one point for 'tricking' voter (unless they voted for their own answer, in which case
                # they get nothing
                room.current_round.give_points(1, guesser)
                break

    if room.current_round.all_votes_in:
        # This was the last voter - move to the reveal
        socketio.send({'event': 'full-reveal', 'room': room.serialize(full=True)}, json=True, to=room.code)
        room.end_round()

    return "Success"


@app.route('/checkRoomCode')
def check_room_code():
    room = _get_room(request.args.get('code'))

    # Handle non-existent room
    if not room:
        return 'false'

    resp = make_response('true')
    resp.set_cookie('room', room.code)
    return resp


@app.route('/startGame')
def start_game():
    # TODO add handling to make sure at least 3 people have joined the room
    room = _get_room(request.args.get('code'))

    # Handle non-existent room
    if not room:
        return 'Room not found'

    room.start()
    resp = make_response(room.serialize())

    socketio.send({'event': 'start-game', 'room': room.serialize()}, json=True, to=room.code)

    # Start the first round
    start_round()

    return resp


@app.route('/startRound', methods=['POST'])
def start_round():
    room_code = request.args.get('code')
    for room in rooms:
        if room.code == room_code:
            # Found the room
            room.start_round()

            # TODO Add handling to ensure the room doesn't ever see the same movie twice
            movie = Movie.get_random()
            room.current_round.movie = movie

            # Send title & plot to host
            socketio.send({'event': 'movie', 'room': room.serialize(), 'title': movie.title, 'plot': movie.plot}, json=True, to=room.current_round.judge.socket_client)

            # Send notification to guessers that the judge is selecting a movie title
            for guesser in room.current_round.guessers:
                socketio.send({'event': 'judge-selecting', 'room': room.serialize()}, json=True,
                              to=guesser.socket_client)

            return 'Started round!'

    return 'Room not found'


@app.route('/skipMovie', methods=['POST'])
def skip_movie():
    """
    The judge didn't like the movie they were presented with, so give them a new one.

    Returns:
        str: response string
    """
    room = _get_room(request.args.get('code'))

    movie = Movie.get_random()
    room.current_round.movie = movie

    # Send title & plot to host
    socketio.send({'event': 'movie', 'room': room.serialize(), 'title': movie.title, 'plot': movie.plot}, json=True, to=room.current_round.judge.socket_client)

    return 'Started round!'


@app.route('/openGuesses', methods=['POST'])
def open_guesses():
    """
    "Opens" the guessing for other users - this means the judge has found a suitable title/plot and is ready for users
    to start guessing.

    Returns:
        Response
    """
    room = _get_room(request.cookies.get('room'))
    room.open_guessing()

    # Send title to rest of users
    for guesser in room.current_round.guessers:
        socketio.send({'event': 'movie-title', 'title': room.current_round.movie.title}, json=True,
                      to=guesser.socket_client)

    return 'Opened guessing!'


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
            if room.current_round and room.current_round.judge and user == room.current_round.judge:
                print(f'This user ({user.name}) is the current judge!')
                # Send full (including current answers) to judge - this handles the judge refreshing their page and
                # "re-joining" the game
                send({'event': 'new-user', 'username': user.name, 'room': room.serialize(full=True)}, json=True, to=room.current_round.judge.socket_client)

                # Send the judge joining event to all other users (but not the judge, or this would wipe the answers
                # the judge has)
                for guesser in room.current_round.guessers:
                    send({'event': 'new-user', 'username': user.name, 'room': room.serialize()}, json=True,
                         to=guesser.socket_client)
            else:
                send({'event': 'new-user', 'username': user.name, 'room': room.serialize()}, json=True, to=room.code)

            print(f'{user.name} joined {room.code} ({user.socket_client})')
            break


@socketio.on('disconnect')
def disconnect():
    print('Disconnected!')


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8010, debug=True)
