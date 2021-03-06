import unittest

from user import User


class TestUser(unittest.TestCase):

    def test_init(self):
        user = User('User123')
        self.assertEqual(user.name, 'User123')

        # Defaults/empty
        self.assertEqual(user.current_score, 0)
        self.assertIsNone(user.current_answer)
        self.assertIsNone(user.current_vote)

    def test_repr(self):
        user = User('User123')
        self.assertEqual(repr(user), 'User123')

    def test_str(self):
        user = User('User123')
        self.assertEqual(str(user), 'User123')

    def test_eq_diff_types(self):
        user1 = User('User123')
        user2 = "I am not a User"

        self.assertNotEqual(user1, user2)

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

    def test_has_answered_no_answer(self):
        user = User('User123')

        self.assertFalse(user.has_answered)

    def test_has_answered_answered(self):
        user = User('User123')
        user.current_answer = 'A really cool and funny plot'

        self.assertTrue(user.has_answered)

    def test_has_voted_no_vote(self):
        user = User('User123')
        user.current_vote = None

        self.assertFalse(user.has_voted)

    def test_has_voted_voted(self):
        user = User('User123')
        user.current_vote = "A reasonable plot"

        self.assertTrue(user.has_voted)

    def test_serialize(self):
        user = User('User123')
        user.current_score = 0
        self.assertEqual(user.serialize(),
                         {'hasAnswered': 'False',
                          'name': 'User123',
                          'score': '0',
                          'vote': ''})

    def test_serialize_score(self):
        user = User('User123')
        user.current_score = 4
        self.assertEqual(user.serialize(),
                         {'hasAnswered': 'False',
                          'name': 'User123',
                          'score': '4',
                          'vote': ''})

    def test_serialize_full_no_answer(self):
        user = User('User123')
        user.current_score = 0
        self.assertEqual(user.serialize(full=True),
                         {'currentAnswer': None,
                          'hasAnswered': 'False',
                          'name': 'User123',
                          'score': '0',
                          'vote': ''})

    def test_serialize_full_with_answer(self):
        user = User('User123')
        user.current_answer = 'A really good guess'
        user.current_score = 0
        self.assertEqual(user.serialize(full=True),
                         {'currentAnswer': 'A really good guess',
                          'hasAnswered': 'True',
                          'name': 'User123',
                          'score': '0',
                          'vote': ''})

    def test_serialize_full_with_vote(self):
        user = User('User123')
        user.current_answer = 'A really good guess'
        user.current_score = 0
        user.current_vote = 'Another really good guess'
        self.assertEqual(user.serialize(full=True),
                         {'currentAnswer': 'A really good guess',
                          'hasAnswered': 'True',
                          'name': 'User123',
                          'score': '0',
                          'vote': 'Another really good guess'})


if __name__ == '__main__':
    unittest.main()
