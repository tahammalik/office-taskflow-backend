"""
    -------exceptions module-------

    This file for defining custom exceptions and their handlers.
    Here we define a custom exception UserNotFoundError and its handler
    it is now basic in future we can add more custom exceptions like InvalidCredentialsError,
    DatabaseError etc and their handlers to provide more specific error messages and status codes
    for different error scenarios.
"""


"""this is for practice later we can more structured and organized way 
to handle exceptions like creating a separate file for exceptions and handlers and also we can use 
logging to log the errors for better debugging and monitoring."""

class UserNotFoundError(Exception):   # custom exception for user not found scenario
    def __init__(self,message):
        self.message = message

class EmailAlreadyExistsError(Exception):  # custom exception for email already exists scenario
    def __init__(self,message):
        self.message = message

