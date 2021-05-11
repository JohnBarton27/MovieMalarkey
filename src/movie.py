from imdb import IMDb
import pathlib
from random import randrange


class Movie:

    # Get location of Movie Malarkey source (for proper retrival of stripped dataset)
    movie_malarkey_loc = pathlib.Path(__file__).parent.absolute().parent.absolute()
    local_datastore = pathlib.Path.joinpath(movie_malarkey_loc, 'dataset/malarkey.tsv')

    ia = IMDb()

    def __init__(self, title: str, year: str, movie_id: str = None):
        """
        Constructor for Movie object

        Args:
            title (str): Title of the Movie
            year (str): Year of the Movie's release. Uses a str for non-standard years ('N/A', 'Unknown', etc.)
            movie_id (str, Optional): IMDb ID of the Movie (if given). Defaults to None
        """
        self.title = title
        self.year = year
        self.id = movie_id
        self._imdbpy_movie = None

    def __repr__(self):
        return f'{self.title} ({self.year})'

    def __str__(self):
        return repr(self)

    @property
    def plot(self):
        raw_plot = self._imdbpy_movie["plot"][0]

        # Some plots seem to use '::' to credit the author of the plot summary
        return raw_plot.split('::')[0]

    def populate(self):
        self._imdbpy_movie = Movie.ia.get_movie(self.id)

    def serialize(self, full=False):
        """
        Serializes the object as JSON.

        Args:
            full (bool): If True, returns all data. If False, does not return the Plot of the Movie. This can be useful
             when hiding the 'correct' plot from the guessers.

        Returns:
            dict: JSON representation of this Movie
        """
        return {
            'title': self.title,
            'plot': self.plot if full else ''
        }

    @staticmethod
    def get_random():
        """
        Gets a random Movie from the local datastore

        Returns:
            Movie: Random Movie object
        """
        with open(Movie.local_datastore, "r") as local_ds:
            content = local_ds.read()
            movies = content.split("\n")[1:]

            num_movies = len(movies)

            selected_index = randrange(num_movies - 1)
            selected = movies[selected_index]

            movie_pieces = selected.split("\t")

            movie_id = movie_pieces[0].split("tt")[-1]
            movie_title = movie_pieces[2]
            movie_year = str(movie_pieces[5])

            movie = Movie(movie_title, movie_year, movie_id=movie_id)
            movie.populate()

            return movie
