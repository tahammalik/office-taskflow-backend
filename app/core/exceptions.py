"""
-------exceptions module-------

This file for defining custom exceptions and their handlers.
Here we define a custom exception UserNotFoundError and its handler
it is now basic in future we can add more custom exceptions like InvalidCredentialsError,
DatabaseError etc and their handlers to provide more specific error messages and status codes
for different error scenarios.
"""


class UserNotFoundError(Exception):  # custom exception for user not found scenario
    def __init__(self, message):
        self.message = message


class EmailAlreadyExistsError(
    Exception
):  # custom exception for email already exists scenario
    def __init__(self, message):
        self.message = message


class AccountLockedError(Exception):
    def __init__(self, message):
        self.message = message
<<<<<<< Updated upstream

class ServerError(Exception):
    def __init__(self, *args):
        self.args = args
=======
>>>>>>> Stashed changes
