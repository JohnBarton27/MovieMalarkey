import unittest
from unittest.mock import call, patch, MagicMock, PropertyMock

from movie import Movie
from room import Room
from user import User


class TestRoom(unittest.TestCase):

    user1 = None
    user2 = None
    user3 = None

    def setUp(self) -> None:
        TestRoom.user1 = User('User123')
        TestRoom.user2 = User('User234')
        TestRoom.user3 = User('User345')

    @patch('room.Room.generate_code')
    def test_init(self, m_gen_code):
        m_gen_code.return_value = 'AB27'

        room = Room(TestRoom.user1)

        self.assertEqual(room.host, TestRoom.user1)
        self.assertEqual(room.users, [TestRoom.user1])
        self.assertEqual(room.code, 'AB27')

        # Defaults/empty
        self.assertEqual(room.rounds, [])
        self.assertFalse(room.started)

    def test_repr(self):
        room = Room(TestRoom.user1)
        room.code = '1234'

        self.assertEqual(repr(room), '1234')

    def test_str(self):
        room = Room(TestRoom.user1)
        room.code = '1234'

        self.assertEqual(str(room), '1234 (Users: 1)')

    def test_eq_equal(self):
        room1 = Room(TestRoom.user1)
        room1.code = '1234'

        room2 = Room(TestRoom.user1)
        room2.code = '1234'

        self.assertEqual(room1, room2)

    def test_eq_neq(self):
        room1 = Room(TestRoom.user1)
        room1.code = '1234'

        room2 = Room(TestRoom.user1)
        room2.code = 'ABCD'

        self.assertNotEqual(room1, room2)

    def test_hash(self):
        room = Room(TestRoom.user1)
        room.code = '1234'

        self.assertEqual(hash(room), hash('1234'))

    @patch('room.Room.current_round', new_callable=PropertyMock)
    def test_all_guesses_submitted_no_submission(self, m_round):
        room = Room(TestRoom.user1)
        room.add_user(TestRoom.user2)
        room.add_user(TestRoom.user3)

        cur_round = MagicMock()
        cur_round.guessers = [TestRoom.user2, TestRoom.user3]
        m_round.return_value = cur_round

        self.assertFalse(room.all_guesses_submitted)
        m_round.assert_called()

    @patch('room.Room.current_round', new_callable=PropertyMock)
    def test_all_guesses_submitted_some_submissions(self, m_round):
        room = Room(TestRoom.user1)
        room.add_user(TestRoom.user2)
        room.add_user(TestRoom.user3)

        cur_round = MagicMock()
        cur_round.guessers = [TestRoom.user2, TestRoom.user3]
        m_round.return_value = cur_round

        TestRoom.user2.current_answer = "A plot for a film"

        self.assertFalse(room.all_guesses_submitted)
        m_round.assert_called()

    @patch('room.Room.current_round', new_callable=PropertyMock)
    def test_all_guesses_submitted_all_submissions(self, m_round):
        room = Room(TestRoom.user1)
        room.add_user(TestRoom.user2)
        room.add_user(TestRoom.user3)

        cur_round = MagicMock()
        cur_round.guessers = [TestRoom.user2, TestRoom.user3]
        m_round.return_value = cur_round

        TestRoom.user2.current_answer = "A plot for a film"
        TestRoom.user3.current_answer = "An even better plot for a movie!"

        self.assertTrue(room.all_guesses_submitted)
        m_round.assert_called()

    def test_current_round_no_rounds(self):
        room = Room(TestRoom.user1)

        self.assertIsNone(room.current_round)

    def test_current_round_one_round(self):
        room = Room(TestRoom.user1)

        round1 = MagicMock()
        room.rounds = [round1]

        self.assertEqual(room.current_round, round1)

    def test_current_round_multiple_rounds(self):
        room = Room(TestRoom.user1)

        round1 = MagicMock()
        round2 = MagicMock()
        round3 = MagicMock()
        room.rounds = [round1, round2, round3]

        self.assertEqual(room.current_round, round3)

    def test_previous_round_no_rounds(self):
        room = Room(TestRoom.user1)

        self.assertIsNone(room.previous_round)

    def test_previous_round_one_round(self):
        room = Room(TestRoom.user1)

        round1 = MagicMock()
        room.rounds = [round1]

        self.assertIsNone(room.previous_round)

    def test_previous_round_two_rounds(self):
        room = Room(TestRoom.user1)

        round1 = MagicMock()
        round2 = MagicMock()
        room.rounds = [round1, round2]

        self.assertEqual(room.previous_round, round1)

    def test_previous_round_three_rounds(self):
        room = Room(TestRoom.user1)

        round1 = MagicMock()
        round2 = MagicMock()
        round3 = MagicMock()
        room.rounds = [round1, round2, round3]

        self.assertEqual(room.previous_round, round2)

    def test_add_user_new_user(self):
        room = Room(TestRoom.user1)
        user2 = User('Jessica')

        room.add_user(user2)
        self.assertEqual(room.users, [TestRoom.user1, user2])

    def test_add_user_existing_user(self):
        room = Room(TestRoom.user1)
        user2 = User('User123')

        room.add_user(user2)
        self.assertEqual(room.users, [TestRoom.user1])

    def test_start_round(self):
        room = Room(TestRoom.user1)

        room.start_round()

        self.assertEqual(len(room.rounds), 1)
        self.assertEqual(room.rounds[0].num, 1)

    def test_start_round_two_rounds(self):
        room = Room(TestRoom.user1)

        room.start_round()
        room.start_round()

        self.assertEqual(len(room.rounds), 2)
        self.assertEqual(room.rounds[0].num, 1)
        self.assertEqual(room.rounds[1].num, 2)

    @patch('room.Room.select_next_judge')
    def test_end_round(self, m_next_judge):
        room = Room(TestRoom.user1)
        user2 = User('User2')
        user3 = User('User3')

        room.add_user(user2)
        room.add_user(user3)

        # Must have a round to end
        round1 = MagicMock()
        room.rounds = [round1]

        TestRoom.user1.current_answer = 'User1\'s answer'
        user2.current_answer = 'An answer from User2'
        user3.current_answer = None

        room.current_judge = user2

        m_next_judge.return_value = None

        room.end_round()

        self.assertIsNone(TestRoom.user1.current_answer)
        self.assertIsNone(user2.current_answer)
        self.assertIsNone(user3.current_answer)

        m_next_judge.assert_called()

    @patch('room.random.choice')
    def test_generate_code(self, m_choice):
        m_choice.side_effect = ['1', 'A', '2', 'B']
        code = Room.generate_code()

        possible_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        m_choice.assert_has_calls([call(possible_chars),
                                   call(possible_chars),
                                   call(possible_chars),
                                   call(possible_chars)])
        self.assertEqual(code, '1A2B')

    @patch('user.User.serialize')
    def test_serialize(self, m_user_serialize):
        room = Room(TestRoom.user1)
        room.code = 'ABCD'

        m_user_serialize.return_value = {'name': 'USER1'}

        correct_serialized = {
            'code': 'ABCD',
            'host': {'name': 'USER1'},
            'round': '',
            'started': 'False',
            'users': [{'name': 'USER1'}]
        }

        self.assertEqual(room.serialize(), correct_serialized)

        m_user_serialize.assert_called_with(full=False)

    @patch('user.User.serialize')
    def test_serialize_full(self, m_user_serialize):
        room = Room(TestRoom.user1)
        room.code = 'ABCD'

        m_user_serialize.return_value = {'name': 'USER1'}

        correct_serialized = {
            'code': 'ABCD',
            'host': {'name': 'USER1'},
            'round': '',
            'started': 'False',
            'users': [{'name': 'USER1'}]
        }

        self.assertEqual(room.serialize(full=True), correct_serialized)

        m_user_serialize.assert_called_with(full=True)

    @patch('user.User.serialize')
    @patch('room.Room.current_round', new_callable=PropertyMock)
    def test_serialize_with_round(self, m_current_round, m_user_serialize):
        room = Room(TestRoom.user1)
        room.code = 'ABCD'

        current_round = MagicMock()
        m_current_round.return_value = current_round
        current_round.serialize.return_value = {'number': '1'}

        m_user_serialize.return_value = {'name': 'USER1'}

        correct_serialized = {
            'code': 'ABCD',
            'host': {'name': 'USER1'},
            'round': {'number': '1'},
            'started': 'False',
            'users': [{'name': 'USER1'}]
        }

        self.assertEqual(room.serialize(), correct_serialized)

        m_user_serialize.assert_called()
        current_round.serialize.assert_called()

    @patch('room.random.choice')
    @patch('room.Room.generate_code')
    def test_start(self, m_generate_code, m_choice):
        room = Room(TestRoom.user1)

        # We don't actually need to test if generate_code() is working, but since we're
        # patching random.choice(), it won't work, so we need to patch it as well
        m_generate_code.assert_called()

        # Room should not be started upon __init__
        self.assertFalse(room.started)

        selected_user = MagicMock()
        m_choice.return_value = selected_user

        room.start()
        m_choice.assert_called_with(room.users)

        self.assertTrue(room.started)
        self.assertEqual(room.current_judge, selected_user)

    def test_stop(self):
        room = Room(TestRoom.user1)
        room.start()

        room.stop()

        self.assertFalse(room.started)

    def test_select_next_judge(self):
        room = Room(TestRoom.user1)
        user2 = User('User2')
        user3 = User('User3')
        room.users = [TestRoom.user1, user2, user3]
        room.current_judge = TestRoom.user1

        room.select_next_judge()

        self.assertEqual(room.current_judge, user2)

    def test_select_next_judge_loop_around(self):
        room = Room(TestRoom.user1)
        user2 = User('User2')
        user3 = User('User3')
        room.users = [TestRoom.user1, user2, user3]
        room.current_judge = user3

        room.select_next_judge()

        self.assertEqual(room.current_judge, TestRoom.user1)

    @patch('room.random.choice')
    @patch('room.Room.generate_code')
    def test_select_next_judge_random(self, m_generate_code, m_choice):
        room = Room(TestRoom.user1)

        # We don't actually need to test if generate_code() is working, but since we're
        # patching random.choice(), it won't work, so we need to patch it as well
        m_generate_code.assert_called()

        user2 = User('User2')
        user3 = User('User3')
        room.users = [TestRoom.user1, user2, user3]
        room.current_judge = None

        m_choice.return_value = user3

        room.select_next_judge()

        m_choice.assert_called_with(room.users)
        self.assertEqual(room.current_judge, user3)


if __name__ == '__main__':
    unittest.main()
