"""
exceptions.py - File that contains all the custom-made exceptions; primarily for http or parsing errors
"""

class HttpError(Exception):
    pass

class ForbiddenError(Exception):
    pass

class NotFoundError(HttpError):
    pass
