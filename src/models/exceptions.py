class APIError(Exception):
    status_code: int | None = None

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class UnauthorizedError(APIError):
    def __init__(self):
        super().__init__("Unauthorized", 401)

class ForbiddenError(APIError):
    def __init__(self):
        super().__init__("Forbidden", 403)

class NotFoundError(APIError):
    def __init__(self):
        super().__init__("Not found", 404)

class ConflictError(APIError):
    def __init__(self):
        super().__init__("Conflict", 409)

class ServerError(APIError):
    def __init__(self):
        super().__init__("Server error", 500)

class NetworkError(APIError):
    def __init__(self):
        super().__init__("Server unavailable")