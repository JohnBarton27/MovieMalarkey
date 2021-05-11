import random
import string

from round import Round
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
        self.rounds = []
        self.code = Room.generate_code()
        self.started = False

    def __repr__(self):
        return self.code

    def __str__(self):
        return f'{self.code} (Users: {len(self.users)})'

    def __eq__(self, other):
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)

    @property
    def all_guesses_submitted(self):
        """
        Checks to see if all guesses for the round have been submitted.

        Returns:
            bool: True if all 'guessers' have submitted an answer; False if at least one has not guessed
        """
        return all(user.current_answer for user in self.current_round.guessers)

    @property
    def current_round(self) -> Round:
        """
        Gets the current (or most recent) round, if there is one.

        Returns:
            Round: Current (or most recent) round
        """
        if len(self.rounds) == 0:
            # No rounds have been started
            return None

        # Return last round
        return self.rounds[-1]

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

    def start_round(self):
        """
        Starts a new round in this room

        Returns:
            None
        """
        self.rounds.append(Round(self, len(self.rounds) + 1))

    def end_round(self):
        """
        Cleanup method for when a round ends (clears all answers, etc.)

        Returns:
            None
        """
        self.rounds[-1].end()

        # Wipe all answers
        for user in self.users:
            user.current_answer = None

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
            'round': self.current_round.serialize(full=full) if self.current_round else '',
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
