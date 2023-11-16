import hashlib
import math
import time

from fastapi import APIRouter

from homework_api import basemodels, db_operations, utils
from homework_api.database import classroom_conn
from homework_api.error_response import ErrorResponse

router = APIRouter(prefix="/homework", tags=["homework"])


@router.post("/add")
async def add_homework(body: basemodels.addHomework):
    cleaned_body = utils.cleanse_api_body(body.model_dump())

    if cleaned_body["assigned_date"] is None:
        cleaned_body["assigned_date"] = time.strftime("%Y-%m-%d")

    # check if assigned_date and due_date is in the correct format
    if not utils.check_valid_dates(
        [cleaned_body["assigned_date"], cleaned_body["due_date"]]
    ):
        return ErrorResponse.DATE_INVALID.value

    encrypted_password = hashlib.sha256(
        cleaned_body["classroom_password"].encode("utf8")
    ).hexdigest()

    # check if classroom secret and password is correct
    classroom_check = await db_operations.get_classroom_password(
        classroom_conn, cleaned_body["classroom_secret"], encrypted_password
    )

    if classroom_check is None:
        return ErrorResponse.SECRET_OR_PASSWORD_INVALID.value

    classroom_id = classroom_check["ClassroomID"]

    if teacher is None:
        teacher_check = await db_operations.get_teacher(
            classroom_conn, classroom_id, cleaned_body["subject"]
        )

        if teacher_check is None:
            return ErrorResponse.NO_TEACHER.value

        teacher = teacher_check["Teacher"]

    # insert into database
    homework_id = await db_operations.add_homework(
        classroom_conn,
        classroom_id,
        cleaned_body["subject"],
        teacher,
        cleaned_body["title"],
        cleaned_body["description"],
        cleaned_body["assigned_date"],
        cleaned_body["due_date"],
    )

    # _RETURN
    return {
        "response_code": 201,
        "response": {
            "context": {
                "homework_id": homework_id,
            },
            "error": None,
            "message": "Homework created successfully",
        },
    }


@router.post("/remove")
async def remove_homework(body: basemodels.removeHomework):
    cleaned_body = utils.cleanse_api_body(body.model_dump())

    encrypted_password = hashlib.sha256(
        cleaned_body["classroom_password"].encode("utf8")
    ).hexdigest()

    # check if classroom secret and password is correct
    classroom_check = await db_operations.get_classroom_password(
        classroom_conn, cleaned_body["classroom_secret"], encrypted_password
    )

    if classroom_check is None:
        return ErrorResponse.SECRET_OR_PASSWORD_INVALID.value

    classroom_id = classroom_check["ClassroomID"]

    # check if homework exists
    homework_check = await db_operations.get_homework(
        classroom_conn, classroom_id, cleaned_body["homework_id"]
    )

    if homework_check is None:
        return ErrorResponse.HOMEWORK_NOT_FOUND.value

    await db_operations.remove_homework(
        classroom_conn, classroom_id, cleaned_body["homework_id"]
    )

    # _RETURN
    return {
        "response_code": 200,
        "response": {
            "context": {
                "deleted_homework_id": cleaned_body["homework_id"],
            },
            "error": None,
            "message": "Homework deleted successfully",
        },
    }


@router.post("/list")
async def list_homeworks(body: basemodels.listHomeworks):
    cleaned_body = utils.cleanse_api_body(body.model_dump())

    cleaned_body["count"] = cleaned_body["count"] or 10
    cleaned_body["page"] = cleaned_body["page"] or 1

    if cleaned_body["count"] > 50:
        return ErrorResponse.TOO_MUCH_COUNT.value

    # Check if assigned_date and due_date is in the correct format
    if not utils.check_valid_dates(
        [
            cleaned_body["assigned_before_date"],
            cleaned_body["assigned_after_date"],
            cleaned_body["due_before_date"],
            cleaned_body["due_after_date"],
        ]
    ):
        return ErrorResponse.DATE_INVALID.value

    # check if classroom secret is correct
    classroom_check = await db_operations.get_classroom_no_password(
        classroom_conn, cleaned_body["classroom_secret"]
    )

    if classroom_check is None:
        return ErrorResponse.SECRET_INVALID.value

    classroom_id = classroom_check["ClassroomID"]

    # get homeworks
    homeworks = await db_operations.get_homeworks(
        classroom_conn,
        classroom_id,
        db_operations.getHomeworksCriteria(
            count=cleaned_body["count"],
            offset=(cleaned_body["page"] - 1) * cleaned_body["count"],
            assigned_before_date=cleaned_body["assigned_before_date"],
            assigned_after_date=cleaned_body["assigned_after_date"],
            due_before_date=cleaned_body["due_before_date"],
            due_after_date=cleaned_body["due_after_date"],
        ),
    )

    homeworks_formatted = [
        {
            "homework_id": homework["HomeworkID"],
            "subject": homework["Subject"],
            "teacher": homework["Teacher"],
            "title": homework["Title"],
            "description": homework["Description"],
            "assigned_date": homework["AssignedDate"],
            "due_date": homework["DueDate"],
        }
        for homework in homeworks
    ]

    # get count of homeworks
    homework_count = await db_operations.get_homeworks_count(
        classroom_conn,
        classroom_id,
        db_operations.getHomeworksCountCriteria(
            assigned_before_date=cleaned_body["assigned_before_date"],
            assigned_after_date=cleaned_body["assigned_after_date"],
            due_before_date=cleaned_body["due_before_date"],
            due_after_date=cleaned_body["due_after_date"],
        ),
    )

    max_page = math.ceil(homework_count["COUNT(HomeworkID)"] / cleaned_body["count"])

    # _RETURN
    return {
        "response_code": 200,
        "response": {
            "context": {
                "homeworks": homeworks_formatted,
                "page": cleaned_body["page"],
                "max_page": max_page,
            },
            "error": None,
            "message": "Homeworks retrieved successfully",
        },
    }


@router.post("/get")
async def get_homework(body: basemodels.getHomework):
    cleaned_body = utils.cleanse_api_body(body.model_dump())

    classroom_check = await db_operations.get_classroom_no_password(
        classroom_conn, cleaned_body["classroom_secret"]
    )

    if classroom_check is None:
        return ErrorResponse.SECRET_INVALID.value

    classroom_id = classroom_check["ClassroomID"]

    homework = await db_operations.get_homework(classroom_conn, classroom_id, cleaned_body["homework_id"])

    if homework is None:
        return ErrorResponse.HOMEWORK_NOT_FOUND.value
    
    return {
        "response_code": 200,
        "response": {
            "context": {
                "homework_id": homework["HomeworkID"],
                "subject": homework["Subject"],
                "teacher": homework["Teacher"],
                "title": homework["Title"],
                "description": homework["Description"],
                "assigned_date": homework["AssignedDate"],
                "due_date": homework["DueDate"],
            },
            "error": None,
            "message": "Homework retrieved successfully",
        },
    }
