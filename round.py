class Round:

    def __init__(self, room, num: int):
        self.room = room
        self.num = num

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
