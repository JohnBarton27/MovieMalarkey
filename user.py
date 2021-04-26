
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

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def serialize(self):
        return {'name': self.name}
