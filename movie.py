from imdb import IMDb
from random import randrange


class Movie:

    local_datastore = "/home/john/git/movie_malarkey/dataset/title.basics.tsv"
    ia = IMDb()

    def __init__(self, title: str, year: str, movie_id: str = None):
        self.title = title
        self.year = year
        self.id = movie_id
        self._imdbpy_movie = None

    def __repr__(self):
        return f'{self.title} ({self.year})'

    def __str__(self):
        return repr(self)

    def populate(self):
        self._imdbpy_movie = Movie.ia.get_movie(self.id)

    @property
    def plot(self): 
        return self._imdbpy_movie["plot"][0] if "plot" in self._imdbpy_movie else None

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

            title_type = None
            found_plot = False

            while title_type != "movie" and not found_plot:
                selected_index = randrange(num_movies - 1)
                selected = movies[selected_index]

                movie_pieces = selected.split("\t")
                title_type = movie_pieces[1]

                if title_type != "movie":
                    continue

                movie_id = movie_pieces[0].split("tt")[-1]
                movie_title = movie_pieces[2]
                print(f"Checking {movie_title}...")
                movie_year = str(movie_pieces[5])

                movie = Movie(movie_title, movie_year, movie_id=movie_id)
                movie.populate()

                found_plot = "plot" in movie._imdbpy_movie

            return movie
