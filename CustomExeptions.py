class AlreadyExistsException(Exception):
    def __init__(self):
        self.text = 'The value already exists in data base'