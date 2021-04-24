from flask import Flask, make_response, render_template, request

from movie import Movie
from room import Room
from user import User

app = Flask(__name__, template_folder='templates')
rooms = []


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
    room = Room(user)
    rooms.append(room)
    return render_template('room.html', room=room)


@app.route('/joinRoom', methods=['POST'])
def join_room():
    user = User(request.cookies.get('user_name'))
    form_data = request.form
    room_code = form_data['Room_Code']

    for room in rooms:
        if room.code == room_code:
            room.add_user(user)
            return render_template('room.html', room=room)

    return f'<h1>No room {room_code} found!</h1>'


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8010, debug=True)
