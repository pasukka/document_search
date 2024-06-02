class DatabaseException(Exception):
    pass

class DBCreationError(DatabaseException):
    def __init__(self):
        self.message = f"Error occurred while creating database!"
        super().__init__(self.message)

class ChatCreationError(DatabaseException):
    def __init__(self, id):
        self.message = f"Error occurred while creating chat {id}!"
        super().__init__(self.message)

class ChatPathError(DatabaseException):
    def __init__(self, id):
        self.message = f"Error occurred while selecting file path of chat {id}!"
        super().__init__(self.message)
