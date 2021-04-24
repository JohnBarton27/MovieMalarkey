import random
import string

from user import User
    

class Room:
    """
    Class for representing "Rooms"
    """
    __rooms = {}
    
    def __init__(self, creator: User):
        """
        Initializer for a Room object

        Args:
            creator (User): User who created the Room
        """
        self.host = creator
        self.users = [creator]
        self.code = Room.__generate_code()
    
    def __repr__(self):
        return self.code

    def __str__(self):
        return f'{self.code} (Users: {len(self.users)})'

    def __eq__(self, other):
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)

    def add_user(self, user: User):
        """
        Add the given user to this Room (handles ensuring no duplicate users)

        Args:
            user (User): User to add to this room

        Returns:
            None
        """
        if user not in self.users:
            self.users.append(user)
    
    """
    TODO: add check to make sure only current host is invoking this method, 
    or the user that is getting removed (e.g. when someone voluntarily leaves the game).
    Might be better to do outside this class
    """ 
    def remove_user(self, user: User):
        """
        Remove the given user from this Room, if they are in it. 
        If this user is the host, the host is reassigned to the next available user.
        If this is the last user in the room, the room is closed
        
        Args:
            user (User): User to remove from this room
            
        Returns:
            None
        """
        if user in self.users:
            self.users.remove(user)
        if len(self.users) == 0:
            self.close_room()
        elif self.host == user:
            # Only change the host if there are other users still in the room
            self.host = self.users[0]
    
    # TODO: add check to make sure only current host is invoking this method (might be better to do outside this class)
    def change_host(self, new_host: User):
        """
        Change the room host to the given user that is already in the room
        
        Args:
            new_host (User): User in the room to make the host
            
        Returns:
            (User): the old host
        """
        old_host = self.host
        if new_host in self.users:
            self.host = new_host
        return old_host
    
    # TODO: Should this just be a destructor? Don't remember if that's a thing in python
    def close_room(self):
        """
        Closes this room
        """
        del Room.__rooms[self.code]
        # TODO: whatever else needs to be done when closing a room
        return
    
    @staticmethod
    def new_room(creator: User):
        """
        Creates a new room and adds it to the static rooms dict
        
        Args:
            creator (User): User who created the room
            
        Returns:
            (Room): newly created room
        """
        room = Room(creator)
        Room.__rooms[room.code] = room
        return room
    
    @staticmethod
    def __generate_code():
        """
        Generates a random room code

        Returns:
            str: Unique room code
        """
        chars = string.ascii_uppercase
        for i in range(0, 10):
            chars += str(i)

        code = ''.join(random.choice(chars) for i in range(4))
        while code in Room.__rooms:
            code = ''.join(random.choice(chars) for i in range(4))
        return code
    
    #TODO: Maybe make this a property getter (currently not sure if that works with @staticmethod)
    @staticmethod
    def get_rooms():
        """
        Gets the dictionary of all rooms in existence
        
        Args:
            None
            
        Returns:
            (dict<string, Room>): Dictionary of all the rooms that are open
        """
        # TODO: make this return a readonly copy
        return Room.__rooms
    
    @staticmethod
    def get_room(code):
        """
        Returns the Room with the given code, or None if it does not exist
        
        Args:
            code (string): the code of the room to get
            
        Returns:
            (Room): the room with the given code, or None if it does not exist
        """
        return Room.__rooms.get(code, None)
    