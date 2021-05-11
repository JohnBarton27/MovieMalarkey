import unittest
from unittest.mock import MagicMock, patch, PropertyMock

from movie import Movie


class TestMovie(unittest.TestCase):

    def setUp(self) -> None:
        self.m_ia = MagicMock()
        Movie.ia = self.m_ia

    def test_init_base(self):
        movie = Movie('Back to the Future', '1985')

        self.assertEqual(movie.title, 'Back to the Future')
        self.assertEqual(movie.year, '1985')
        self.assertIsNone(movie.id)
        self.assertIsNone(movie._imdbpy_movie)

    def test_init_full(self):
        movie = Movie('Back to the Future', '1985', movie_id='abc123')

        self.assertEqual(movie.title, 'Back to the Future')
        self.assertEqual(movie.year, '1985')
        self.assertEqual(movie.id, 'abc123')
        self.assertIsNone(movie._imdbpy_movie)

    def test_repr(self):
        movie = Movie('Back to the Future', '1985')

        self.assertEqual(repr(movie), 'Back to the Future (1985)')

    def test_eq(self):
        movie = Movie('Back to the Future', '1985')

        self.assertEqual(str(movie), repr(movie))

    def test_plot_no_separator(self):
        movie = Movie('Back to the Future', '1985')
        movie._imdbpy_movie = {
            'plot': ['A time traveller almost erases himself']
        }

        self.assertEqual(movie.plot, 'A time traveller almost erases himself')

    def test_plot_separator(self):
        movie = Movie('Back to the Future', '1985')
        movie._imdbpy_movie = {
            'plot': ['A time traveller almost erases himself::Anonymous']
        }

        self.assertEqual(movie.plot, 'A time traveller almost erases himself')

    def test_populate(self):
        movie = Movie('Back to the Future', '1985')

        imdby_movie = MagicMock()
        self.m_ia.get_movie.return_value = imdby_movie

        movie.populate()

        self.assertEqual(movie._imdbpy_movie, imdby_movie)
        self.m_ia.get_movie.assert_called()

    @patch('movie.Movie.plot', new_callable=PropertyMock)
    def test_serialize_not_full(self, m_plot):
        movie = Movie('Back to the Future', '1985')

        ser = {'title': 'Back to the Future', 'plot': ''}

        self.assertEqual(movie.serialize(), ser)
        m_plot.assert_not_called()

    @patch('movie.Movie.plot', new_callable=PropertyMock)
    def test_serialize_full(self, m_plot):
        movie = Movie('Back to the Future', '1985')
        m_plot.return_value = 'A time traveller almost erases himself'

        ser = {'title': 'Back to the Future', 'plot': 'A time traveller almost erases himself'}

        self.assertEqual(movie.serialize(full=True), ser)
        m_plot.assert_called()


if __name__ == '__main__':
    unittest.main()
