import hashlib
import re
import time

from fastapi import APIRouter

from homework_api import basemodels, db_operations, utils
from homework_api.database import classroom_conn
from homework_api.error_response import ErrorResponse

router = APIRouter(prefix="/classroom", tags=["classroom"])


@router.post("/new")
async def new_classroom(body: basemodels.newClassroom):
    cleaned_body = utils.cleanse_api_body(body.model_dump())

    # check if classroom name and password is valid (3 < len < 10 and have num/num)
    if (
        re.fullmatch(r".{3,10}", cleaned_body["classroom_name"]) is None
        or re.search(r"[1-6]/[0-9]+", cleaned_body["classroom_name"]) is None
    ):
        return ErrorResponse.CLASSROOM_INVALID.value

    if (
        re.fullmatch(r".{5,}", cleaned_body["classroom_password"]) is None
        or re.fullmatch(r"[a-zA-Z0-9]+", cleaned_body["classroom_password"]) is None
    ):
        return ErrorResponse.PASSWORD_INVALID.value

    # classroom secret (username that use to login)
    classroom_secret = hashlib.sha256(
        (cleaned_body["classroom_name"] + str(time.time())).encode("utf8")
    ).hexdigest()

    # classroom password
    encrypted_password = hashlib.sha256(
        cleaned_body["classroom_password"].encode("utf8")
    ).hexdigest()

    # insert into database
    await db_operations.add_classroom(
        classroom_conn,
        classroom_secret,
        encrypted_password,
        cleaned_body["classroom_name"],
    )

    # _RETURN
    return {
        "response_code": 201,
        "response": {
            "context": {
                "classroom_secret": classroom_secret,
            },
            "error": None,
            "message": "Classroom created successfully",
        },
    }
