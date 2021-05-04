import random
import string

from user import User


class Room:
    """
    Class for representing "Rooms"
    """

    def __init__(self, creator: User):
        """
        Initializer for a Room object

        Args:
            creator (User): User who created the Room
        """
        self.host = creator
        self.users = [creator]
        self.code = Room.generate_code()
        self.current_judge = None
        self.started = False
        self.current_movie = None

    def __repr__(self):
        return self.code

    def __str__(self):
        return f'{self.code} (Users: {len(self.users)})'

    def __eq__(self, other):
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)

    @property
    def guessers(self):
        """
        Gets all guessers (everyone but the current judge). Can be useful when sending two different socket events -
        one to the judge, and one to the guessers (less information, etc.)

        Returns:
            list: List of User objects
        """
        guessers = []

        if not self.current_judge:
            # If there is no judge, treat everyone as a guesser
            return self.users

        for user in self.users:
            if user != self.current_judge:
                guessers.append(user)

        return guessers

    @property
    def all_guesses_submitted(self):
        """
        Checks to see if all guesses for the round have been submitted.

        Returns:
            bool: True if all 'guessers' have submitted an answer; False if at least one has not guessed
        """
        return all(user.current_answer for user in self.guessers)

    def add_user(self, user: User):
        """
        Add the given user to this Room (handles ensuring no duplicate users)

        Args:
            user (User): User to add to this room

        Returns:
            None
        """
        # TODO add handling to stop users from joining an already-started game ('Spectator' mode?)
        if user not in self.users:
            self.users.append(user)
            return

        # Ensure user is fully populated
        if user.socket_client:
            for existing_user in self.users:
                if existing_user == user:
                    existing_user.socket_client = user.socket_client
                    return

    def end_round(self):
        """
        Cleanup method for when a round ends (clears all answers, etc.)

        Returns:
            None
        """
        # Wipe all answers
        for user in self.users:
            user.current_answer = None

        self.current_movie = None

        self.select_next_judge()

    @staticmethod
    def generate_code():
        """
        Generates a random room code

        Returns:
            str: Unique room code
        """
        chars = string.ascii_uppercase
        for i in range(0, 10):
            chars += str(i)

        code = ''.join(random.choice(chars) for i in range(4))
        # TODO ensure code is not already in use
        return code

    def serialize(self, full=False):
        return {
            'code': self.code,
            'host': self.host.serialize(),
            'judge': self.current_judge.serialize(full=full) if self.current_judge else '',
            'movie': self.current_movie.serialize() if self.current_movie else '',
            'started': str(self.started),
            'users': [user.serialize(full=full) for user in self.users]
        }

    def start(self):
        """
        Starts a game in this room

        Returns:
            None
        """
        self.started = True

        # Randomly select first judge
        self.current_judge = random.choice(self.users)

    def stop(self):
        """
        Stops/Ends the game in this room

        Returns:
            None
        """
        self.started = False

    def select_next_judge(self):
        if not self.current_judge:
            # If we somehow don't already have a judge, pick a random user from the room
            self.current_judge = random.choice(self.users)
            return

        index = self.users.index(self.current_judge)
        index += 1
        if index == len(self.users):
            # We were at the 'last' user, so loop around & restart
            self.current_judge = self.users[0]
            return

        self.current_judge = self.users[index]
