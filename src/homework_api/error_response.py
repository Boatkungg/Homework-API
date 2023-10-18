from enum import Enum


class ErrorResponse(Enum):
    CLASSROOM_INVALID = {
        "response_code": 400,
        "response": {
            "error": "CLASSROOM_INVALID",
            "message": "Classroom name must be 3-10 characters long and in the format like '4/5....'",
        },
    }

    PASSWORD_INVALID = {
        "response_code": 400,
        "response": {
            "error": "PASSWORD_INVALID",
            "message": "Classroom password must be at least 5 characters long and alphanumeric a-Z 0-9",
        },
    }

    DATE_INVALID = {
        "response_code": 400,
        "response": {
            "error": "DATE_INVALID",
            "message": "Assigned date or due date is invalid",
        },
    }

    SECRET_INVALID = {
        "response_code": 401,
        "response": {
            "error": "SECRET_INVALID",
            "message": "Classroom secret is invalid",
        },
    }

    SECRET_OR_PASSWORD_INVALID = {
        "response_code": 401,
        "response": {
            "error": "SECRET_OR_PASSWORD_INVALID",
            "message": "Classroom secret or password is invalid",
        },
    }

    HOMEWORK_NOT_FOUND = {
        "response_code": 404,
        "response": {
            "error": "HOMEWORK_NOT_FOUND",
            "message": "Homework not found",
        },
    }
