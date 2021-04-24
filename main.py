from flask import Flask, render_template, request

from movie import Movie
from user import User

app = Flask(__name__, template_folder='templates')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/roomSearch', methods=['POST'])
def new_user():
    form_data = request.form
    user = User(form_data['Nickname'])
    return user.name


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8010, debug=True)
