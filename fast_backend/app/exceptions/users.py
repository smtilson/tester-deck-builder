class ValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = errors