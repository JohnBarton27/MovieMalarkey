import unittest
from unittest.mock import patch, MagicMock

from room import Room
from round import Round
from user import User


class TestRound(unittest.TestCase):

    user1 = None
    user2 = None
    user3 = None

    room1 = None
    room2 = None

    def setUp(self) -> None:
        TestRound.user1 = User('user1')
        TestRound.user2 = User('user2')
        TestRound.user3 = User('user3')

        TestRound.room1 = Room(TestRound.user1)
        TestRound.room1.code = 'RM01'
        TestRound.room1.add_user(TestRound.user2)
        TestRound.room1.add_user(TestRound.user3)

        TestRound.room2 = Room(TestRound.user1)
        TestRound.room2.code = 'RM02'
        TestRound.room2.add_user(TestRound.user2)
        TestRound.room2.add_user(TestRound.user3)

    def test_init(self):
        round1 = Round(TestRound.room1, 1)

        self.assertEqual(round1.room, TestRound.room1)
        self.assertEqual(round1.num, 1)

        scores = {
            TestRound.user1: 0,
            TestRound.user2: 0,
            TestRound.user3: 0
        }

        self.assertEqual(round1.scores, scores)
        self.assertIsNone(round1.movie)
        self.assertIsNone(round1.judge)

    def test_repr(self):
        round1 = Round(TestRound.room1, 1)

        self.assertEqual(repr(round1), '1')

    @patch('room.Room.__repr__')
    def test_str(self, m_room_repr):
        round1 = Round(TestRound.room1, 1)

        m_room_repr.return_value = 'RM01'

        self.assertEqual(str(round1), 'RM01 - Round 1')

        m_room_repr.assert_called()

    def test_eq_equal(self):
        round1 = Round(TestRound.room1, 1)
        round2 = Round(TestRound.room1, 1)

        self.assertEqual(round1, round2)

    def test_eq_diff_types(self):
        round1 = Round(TestRound.room1, 1)
        round2 = 'I am a string'

        self.assertNotEqual(round1, round2)

    def test_eq_diff_rooms(self):
        round1 = Round(TestRound.room1, 1)
        round2 = Round(TestRound.room2, 1)

        self.assertNotEqual(round1, round2)

    def test_eq_diff_numbers(self):
        round1 = Round(TestRound.room1, 1)
        round2 = Round(TestRound.room1, 2)

        self.assertNotEqual(round1, round2)

    @patch('room.Room.__hash__')
    def test_hash(self, m_room_hash):
        round1 = Round(TestRound.room1, 1)

        m_room_hash.return_value = 123

        self.assertEqual(hash(round1), hash(f'{hash(123)}1'))

        m_room_hash.assert_called()

    def test_guessers_with_judge(self):
        round1 = Round(TestRound.room1, 1)
        round1.judge = TestRound.user2

        guessers = round1.guessers

        self.assertEqual(guessers, [TestRound.user1, TestRound.user3])

    def test_guessers_no_judge(self):
        round1 = Round(TestRound.room1, 1)

        guessers = round1.guessers

        self.assertEqual(guessers, [TestRound.user1, TestRound.user2, TestRound.user3])

    def test_give_points(self):
        round1 = Round(TestRound.room1, 1)

        round1.give_points(3, TestRound.user2)

        scores = {
            TestRound.user1: 0,
            TestRound.user2: 3,
            TestRound.user3: 0
        }

        self.assertEqual(round1.scores, scores)

    def test_end(self):
        round1 = Round(TestRound.room1, 1)

        scores = {
            TestRound.user1: 3,
            TestRound.user2: 2,
            TestRound.user3: 1
        }

        # Set initial scores
        TestRound.user1.current_score = 10
        TestRound.user2.current_score = 15
        TestRound.user3.current_score = 20

        round1.scores = scores

        round1.end()

        # New scores
        self.assertEqual(TestRound.user1.current_score, 13)
        self.assertEqual(TestRound.user2.current_score, 17)
        self.assertEqual(TestRound.user3.current_score, 21)

        # Voting
        self.assertFalse(TestRound.user1.has_voted)
        self.assertFalse(TestRound.user2.has_voted)
        self.assertFalse(TestRound.user3.has_voted)

    def test_end_with_votes(self):
        round1 = Round(TestRound.room1, 1)

        scores = {
            TestRound.user1: 3,
            TestRound.user2: 2,
            TestRound.user3: 1
        }

        # Set initial scores
        TestRound.user1.current_score = 10
        TestRound.user2.current_score = 15
        TestRound.user3.current_score = 20

        round1.scores = scores

        # Set voting
        TestRound.user1.has_voted = True
        TestRound.user2.has_voted = True
        TestRound.user3.has_voted = True

        round1.end()

        # New scores
        self.assertEqual(TestRound.user1.current_score, 13)
        self.assertEqual(TestRound.user2.current_score, 17)
        self.assertEqual(TestRound.user3.current_score, 21)

        # Voting
        self.assertFalse(TestRound.user1.has_voted)
        self.assertFalse(TestRound.user2.has_voted)
        self.assertFalse(TestRound.user3.has_voted)

    def test_serialize_no_movie(self):
        round1 = Round(TestRound.room1, 1)

        ser = {
            'judge': '',
            'movie': '',
            'number': 1
        }

        self.assertEqual(round1.serialize(), ser)

    def test_serialize_full(self):
        round1 = Round(TestRound.room1, 1)
        movie = MagicMock()
        movie.serialize.return_value = 'A movie'
        round1.movie = movie

        ser = {
            'judge': '',
            'movie': 'A movie',
            'number': 1
        }

        self.assertEqual(round1.serialize(full=True), ser)
        movie.serialize.assert_called_with(full=True)

    def test_serialize_not_full(self):
        round1 = Round(TestRound.room1, 1)
        movie = MagicMock()
        movie.serialize.return_value = 'A movie'
        round1.movie = movie

        ser = {
            'judge': '',
            'movie': 'A movie',
            'number': 1
        }

        self.assertEqual(round1.serialize(full=False), ser)
        movie.serialize.assert_called_with(full=False)

    @patch('user.User.serialize')
    def test_serialize_with_judge(self, m_user_serialize):
        round1 = Round(TestRound.room1, 1)

        m_user_serialize.return_value = {'name': 'USER1'}
        round1.judge = TestRound.user1

        correct_serialized = {
            'judge': {'name': 'USER1'},
            'movie': '',
            'number': 1
        }

        self.assertEqual(round1.serialize(), correct_serialized)

        m_user_serialize.assert_called()


if __name__ == '__main__':
    unittest.main()
