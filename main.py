from flask import Flask, render_template

from movie import Movie

app = Flask(__name__, template_folder='templates')


@app.route("/")
def index():
    # m = Movie.get_random()
    # html = f"""
    # <h1 style="text-align: center;">{m.title} ({m.year})</h1>
    # <hr>
    # <p style="text-align: center;">{m.plot}</p>
    # """
    # return html
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8010, debug=True)
