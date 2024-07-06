class ApplicationException(Exception):
    """
    Base class for exceptions in this module.
    """
    pass



class APIRequestError(ApplicationException):
    """
    Exception for when the API request fails.
    """
    pass

class APISearchError(ApplicationException):
    """
    Exception for when the API search fails.
    """
    pass

class APIRateLimitError(ApplicationException):
    """
    Exception for when the API rate limit is exceeded.
    """
    pass



class DatabaseError(ApplicationException):
    """
    Exception for when the database fails.
    """
    pass

class ElementNotFound(DatabaseError):
    """
    Exception for when an element is not found in the database.
    """
    pass

class ElementInvalid(DatabaseError):
    """
    Exception for when an element is invalid.
    """
    pass