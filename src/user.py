
class User:
    """
    Class for representing Users
    """

    def __init__(self, name: str):
        """
        Initializer for User object

        Args:
            name (str): Name of the User
        """
        self.name = name
        self.current_score = 0
        self.socket_client = None
        self.current_answer = None
        self.current_vote = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        # Must be the same type
        if not isinstance(other, User):
            return False

        # Check for name equivalence
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    @property
    def has_answered(self):
        return self.current_answer is not None

    @property
    def has_voted(self):
        return self.current_vote is not None

    def serialize(self, full=False):
        # This is what is seen by "default" (no cheating on guesses, etc.)
        serialized = {
            'hasAnswered': str(self.has_answered),
            'name': self.name,
            'score': str(self.current_score),
            'vote': self.current_vote if full and self.has_voted else ''
        }

        if full:
            serialized['currentAnswer'] = self.current_answer

        return serialized
