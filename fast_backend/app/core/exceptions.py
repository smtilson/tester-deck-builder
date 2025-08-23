# app/core/exceptions.py


class NotFoundException(Exception):
    def __init__(self, message: str = "Record not found"):
        self.message = message
        super().__init__(self.message)
