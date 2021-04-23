import unittest
from unittest.mock import call, patch

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


if __name__ == '__main__':
    unittest.main()
