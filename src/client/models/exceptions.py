class APIException(Exception):
    pass

# ------------ NETWORK ERRORS ------------

class NetworkError(APIException):
    def __init__(self, details: str):
        self.details = details
        super().__init__(details)

# ------------ HTTP ERRORS ------------

class HTTPError(APIException):
    def __init__(self, status_code: int, details: str):
        self.status_code = status_code
        self.details = details
        super().__init__(details)

class BadRequestError(HTTPError):
    def __init__(self, details = "Bad request"):
        super().__init__(400, details)

class UnauthorizedError(HTTPError):
    def __init__(self, details = "Unauthorized"):
        super().__init__(401, details)

class ForbiddenError(HTTPError):
    def __init__(self, details = "Forbidden"):
        super().__init__(403, details)

class NotFoundError(HTTPError):
    def __init__(self, details: str = "Not found"):
        super().__init__(404, details)

class ConflictError(HTTPError):
    def __init__(self, details: str = "Conflict"):
        super().__init__(409, details)

class ServerError(HTTPError):
    def __init__(self, details: str = "Server error"):
        super().__init__(500, details)