import unittest

from user import User


class TestUser(unittest.TestCase):

    def test_init(self):
        user = User('User123')
        self.assertEqual(user.name, 'User123')
        self.assertEqual(user.current_score, 0)

    def test_repr(self):
        user = User('User123')
        self.assertEqual(repr(user), 'User123')

    def test_str(self):
        user = User('User123')
        self.assertEqual(str(user), 'User123')

    def test_eq_equals(self):
        user1 = User('User123')
        user2 = User('User123')
        self.assertEqual(user1, user2)

    def test_eq_neq(self):
        user1 = User('User123')
        user2 = User('User456')
        self.assertNotEqual(user1, user2)

    def test_hash(self):
        user = User('User123')
        self.assertEqual(hash(user), hash('User123'))


if __name__ == '__main__':
    unittest.main()
