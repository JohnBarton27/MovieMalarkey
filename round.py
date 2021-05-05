class Round:

    def __init__(self, room, num: int):
        self.room = room
        self.num = num
        self.scores = {}

        for user in room.users:
            self.scores[user] = 0

    def __repr__(self):
        return str(self.num)

    def __str__(self):
        return f'{repr(self.room)} - Round {self.num}'

    def __eq__(self, other):
        # Check for type equivalence
        if not isinstance(other, Round):
            return False

        return self.room == other.room and self.num == other.num

    def __hash__(self):
        return hash(f'{hash(self.room)}{self.num}')

    def give_points(self, points: int, user):
        """
        Give points to the given user

        Args:
            points (int): Number of points to give to the passed user
            user (User): User to give points to

        Returns:
            None
        """
        self.scores[user] += points

    def end(self):
        """
        Ends the Round. This applies the current Round's scores to the user's 'full' scores in the Room.

        Returns:
            None
        """
        for user in self.scores:
            user.current_score += self.scores[user]