import unittest
from unittest.mock import call, patch, MagicMock

from room import Room
from user import User


class TestRoom(unittest.TestCase):

    user1 = None

    def setUp(self) -> None:
        TestRoom.user1 = User('User123')

    @patch('room.Room.generate_code')
    def test_init(self, m_gen_code):
        m_gen_code.return_value = 'AB27'

        room = Room(TestRoom.user1)

        self.assertEqual(room.host, TestRoom.user1)
        self.assertEqual(room.users, [TestRoom.user1])
        self.assertEqual(room.code, 'AB27')

        # Defaults/empty
        self.assertFalse(room.started)
        self.assertIsNone(room.current_judge)

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

    @patch('user.User.serialize')
    def test_serialize(self, m_user_serialize):
        room = Room(TestRoom.user1)
        room.code = 'ABCD'

        m_user_serialize.return_value = {'name': 'USER1'}

        correct_serialized = {
            'code': 'ABCD',
            'host': {'name': 'USER1'},
            'judge': '',
            'started': 'False',
            'users': [{'name': 'USER1'}]
        }

        self.assertEqual(room.serialize(), correct_serialized)

        m_user_serialize.assert_called()

    @patch('user.User.serialize')
    def test_serialize_with_judge(self, m_user_serialize):
        room = Room(TestRoom.user1)
        room.code = 'ABCD'

        m_user_serialize.return_value = {'name': 'USER1'}
        room.current_judge = TestRoom.user1

        correct_serialized = {
            'code': 'ABCD',
            'host': {'name': 'USER1'},
            'judge': {'name': 'USER1'},
            'started': 'False',
            'users': [{'name': 'USER1'}]
        }

        self.assertEqual(room.serialize(), correct_serialized)

        m_user_serialize.assert_called()

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
