class Round:

    def __init__(self, room, num: int):
        self.room = room
        self.num = num
        self.scores = {}
        self.movie = None
        self.judge = None

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

    @property
    def guessers(self):
        """
        Gets all guessers (everyone but the current judge). Can be useful when sending two different socket events -
        one to the judge, and one to the guessers (less information, etc.)

        Returns:
            list: List of User objects
        """
        guessers = []

        if not self.judge:
            # If there is no judge, treat everyone as a guesser
            return self.room.users

        for user in self.room.users:
            if user != self.judge:
                guessers.append(user)

        return guessers

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

    def serialize(self, full=False):
        return {
            'number': self.num,
            'judge': self.judge.serialize(full=full) if self.judge else '',
            'movie': self.movie.serialize(full=full) if self.movie else ''
        }
