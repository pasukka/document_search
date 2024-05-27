class SearchingException(Exception):
    pass


class FileError(SearchingException):
    def __init__(self):
        self.message = f"File loading error!"
        super().__init__(self.message)


class TimeError(SearchingException):
    def __init__(self):
        super().__init__(f"Too many requests.")


class TokenError(SearchingException):
    def __init__(self):
        super().__init__(f"Token expired.")
