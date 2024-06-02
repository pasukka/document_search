class DatabaseException(Exception):
    pass


class DBCreationError(DatabaseException):
    def __init__(self):
        self.message = f"Error occurred while creating database!"
        super().__init__(self.message)


class DBClosingError(DatabaseException):
    def __init__(self):
        self.message = f"Error occurred while closing database!"
        super().__init__(self.message)


class ChatCreationError(DatabaseException):
    def __init__(self, id):
        self.message = f"Error occurred while creating chat {id}!"
        super().__init__(self.message)


class AdminCreationError(DatabaseException):
    def __init__(self):
        self.message = f"Error occurred while creating admin!"
        super().__init__(self.message)


class ChatDeletionError(DatabaseException):
    def __init__(self, id):
        self.message = f"Error occurred while deleting chat {id}!"
        super().__init__(self.message)


class ChatPathError(DatabaseException):
    def __init__(self, id):
        self.message = f"Error occurred while selecting file path of chat {id}!"
        super().__init__(self.message)


class NoChatError(DatabaseException):
    def __init__(self, id):
        self.message = f"No chat {id} in database!"
        super().__init__(self.message)
