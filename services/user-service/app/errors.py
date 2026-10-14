"""Domain errors, each mapped to an HTTP status and a stable error code."""


class AppError(Exception):
    status_code = 400
    code = "BAD_REQUEST"

    def __init__(self, message: str, details: list | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or []


class UserNotFoundError(AppError):
    status_code = 404
    code = "USER_NOT_FOUND"


class DuplicateEmailError(AppError):
    status_code = 409
    code = "EMAIL_ALREADY_EXISTS"


class InvalidStateTransitionError(AppError):
    status_code = 409
    code = "INVALID_STATE_TRANSITION"


class UserInactiveError(AppError):
    status_code = 409
    code = "USER_INACTIVE"
