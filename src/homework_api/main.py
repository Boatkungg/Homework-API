from fastapi import FastAPI
import hashlib
import time
from databases import Database
import re

from homework_api import basemodels, utils
from homework_api.error_response import ErrorResponse

app = FastAPI()

database = Database("sqlite:///database.db", force_rollback=True)


@app.on_event("startup")
async def startup():
    await database.connect()

    # create tables if not exists
    await database.execute(
        """CREATE TABLE IF NOT EXISTS classrooms (
                           ClassroomID INTEGER PRIMARY KEY AUTOINCREMENT,
                           ClassroomSecret TEXT NOT NULL,
                           ClassroomPassword TEXT NOT NULL,
                           ClassroomName TEXT NOT NULL
                           )"""
    )

    await database.execute(
        """CREATE TABLE IF NOT EXISTS homeworks (
                           HomeworkID INTEGER PRIMARY KEY AUTOINCREMENT,
                           ClassroomID INTEGER NOT NULL,
                           Subject TEXT NOT NULL,
                           Teacher TEXT NOT NULL,
                           Title TEXT NOT NULL,
                           Description TEXT NOT NULL,
                           AssignedDate DATE NOT NULL,
                           DueDate DATE NOT NULL
                           )"""
    )


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/api/new_classroom")
async def new_classroom(body: basemodels.newClassroom):
    (
        classroom_name,
        classroom_password,
    ) = utils.normalize_strings(
        [
            body.classroom_name,
            body.classroom_password,
        ]
    )

    if (
        re.fullmatch(r".{3,10}", classroom_name) is None
        or re.search(r"[1-6]/[0-9]+", classroom_name) is None
    ):
        return ErrorResponse.CLASSROOM_INVALID.value

    if (
        re.fullmatch(r".{5,}", classroom_password) is None
        or re.fullmatch(r"[a-zA-Z0-9]+", classroom_password) is None
    ):
        return ErrorResponse.PASSWORD_INVALID.value

    # classroom secret (username that use to login)
    classroom_secret = hashlib.sha256(
        (classroom_name + str(time.time())).encode("utf8")
    ).hexdigest()

    # classroom password
    classroom_password_encrypted = hashlib.sha256(
        classroom_password.encode("utf8")
    ).hexdigest()

    # insert into database
    await database.execute(
        """
        INSERT INTO classrooms(
            ClassroomSecret, 
            ClassroomPassword, 
            ClassroomName
        ) VALUES (
            :secret, 
            :password, 
            :name
        )
        """,
        {
            "secret": classroom_secret,
            "password": classroom_password_encrypted,
            "name": classroom_name,
        },
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


@app.post("/api/add_homework")
async def add_homework(body: basemodels.addHomework):
    # WTF
    (
        classroom_secret,
        classroom_password,
        subject,
        teacher,
        title,
        description,
        assigned_date,
        due_date,
    ) = utils.normalize_strings(
        [
            body.classroom_secret,
            body.classroom_password,
            body.subject,
            body.teacher,
            body.title,
            body.description,
            body.assigned_date,
            body.due_date,
        ]
    )

    if assigned_date is None:
        assigned_date = time.strftime("%Y-%m-%d")

    # check if assigned_date and due_date is in the correct format
    if (
        utils.check_valid_date(assigned_date) is False
        or utils.check_valid_date(due_date) is False
    ):
        return ErrorResponse.DATE_INVALID.value

    classroom_password_encrypted = hashlib.sha256(
        classroom_password.encode("utf8")
    ).hexdigest()

    # check if classroom secret and password is correct
    classroom_check = await database.fetch_one(
        """
        SELECT * 
        FROM classrooms 
        WHERE ClassroomSecret = :secret 
        AND ClassroomPassword = :password
        """,
        {"secret": classroom_secret, "password": classroom_password_encrypted},
    )

    if classroom_check is None:
        return ErrorResponse.SECRET_OR_PASSWORD_INVALID.value

    classroom_id = classroom_check["ClassroomID"]

    # insert into database
    homework_id = await database.execute(
        """
        INSERT INTO homeworks(
            ClassroomID, 
            Subject, 
            Teacher, 
            Title, 
            Description, 
            AssignedDate, 
            DueDate
        ) VALUES (
            :classroom_id, 
            :subject, 
            :teacher, 
            :title, 
            :description, 
            :assigned_date, 
            :due_date
        )
        """,
        {
            "classroom_id": classroom_id,
            "subject": subject,
            "teacher": teacher,
            "title": title,
            "description": description,
            "assigned_date": assigned_date,
            "due_date": due_date,
        },
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


@app.post("/api/remove_homework")
async def remove_homework(body: basemodels.removeHomework):
    homework_id = body.homework_id

    # AGAIN??
    (
        classroom_secret,
        classroom_password,
    ) = utils.normalize_strings(
        [
            body.classroom_secret,
            body.classroom_password,
        ]
    )

    classroom_password_encrypted = hashlib.sha256(
        classroom_password.encode("utf8")
    ).hexdigest()

    # check if classroom secret and password is correct
    classroom_check = await database.fetch_one(
        """
        SELECT * 
        FROM classrooms 
        WHERE ClassroomSecret = :secret 
        AND ClassroomPassword = :password
        """,
        {"secret": classroom_secret, "password": classroom_password_encrypted},
    )

    if classroom_check is None:
        return ErrorResponse.SECRET_OR_PASSWORD_INVALID.value

    classroom_id = classroom_check["ClassroomID"]

    # check if homework exists
    homework_check = await database.fetch_one(
        """
        SELECT * 
        FROM homeworks 
        WHERE HomeworkID = :homework_id 
        AND ClassroomID = :classroom_id
        """,
        {"homework_id": homework_id, "classroom_id": classroom_id},
    )

    if homework_check is None:
        return ErrorResponse.HOMEWORK_NOT_FOUND.value

    # delete homework
    await database.execute(
        """
        DELETE FROM homeworks 
        WHERE HomeworkID = :homework_id 
        AND ClassroomID = :classroom_id
        """,
        {"homework_id": homework_id, "classroom_id": classroom_id},
    )

    # _RETURN
    return {
        "response_code": 200,
        "response": {
            "context": {
                "deleted_homework_id": homework_id,
            },
            "error": None,
            "message": "Homework deleted successfully",
        },
    }


@app.post("/api/get_homeworks")
async def get_homeworks(body: basemodels.getHomeworks):
    count = body.count or 10
    page = body.page or 1  # But will be 0 in the query if its 1

    if count > 50:
        return ErrorResponse.TOO_MUCH_COUNT.value

    # Normalize strings
    (
        classroom_secret,
        assigned_before_date,
        assigned_after_date,
        due_before_date,
        due_after_date,
    ) = utils.normalize_strings(
        [
            body.classroom_secret,
            body.assigned_before_date,
            body.assigned_after_date,
            body.due_before_date,
            body.due_after_date,
        ],
    )

    # Check if assigned_date and due_date is in the correct format
    date_fields = [
        assigned_before_date,
        assigned_after_date,
        due_before_date,
        due_after_date,
    ]

    if any(
        utils.check_valid_date(date) is False
        for date in date_fields
        if date is not None
    ):
        return ErrorResponse.DATE_INVALID.value

    use_assigned_before_date = assigned_before_date is not None
    use_assigned_after_date = assigned_after_date is not None
    use_due_before_date = due_before_date is not None
    use_due_after_date = due_after_date is not None

    # check if classroom secret and password is correct
    classroom_check = await database.fetch_one(
        "SELECT * FROM classrooms WHERE ClassroomSecret = :secret",
        {"secret": classroom_secret},
    )

    if classroom_check is None:
        return ErrorResponse.SECRET_INVALID.value

    classroom_id = classroom_check["ClassroomID"]

    # queries
    query = f"""
            SELECT * FROM homeworks 
            WHERE ClassroomID = :classroom_id 
            {
                'AND AssignedDate <= :assigned_before_date' 
                if use_assigned_before_date 
                else ''
            }
            {
                'AND AssignedDate >= :assigned_after_date'
                if use_assigned_after_date 
                else ''
            }
            {
                'AND DueDate <= :due_before_date'
                if use_due_before_date 
                else ''
            }
            {
                'AND DueDate >= :due_after_date'
                if use_due_after_date 
                else ''
            }
            ORDER BY HomeworkID DESC
            LIMIT :count
            OFFSET :offset
            """

    query_dict = {
        "classroom_id": classroom_id,
        "count": count,
        "offset": (page - 1) * count,
    }

    if use_assigned_before_date:
        query_dict["assigned_before_date"] = assigned_before_date

    if use_assigned_after_date:
        query_dict["assigned_after_date"] = assigned_after_date

    if use_due_before_date:
        query_dict["due_before_date"] = due_before_date

    if use_due_after_date:
        query_dict["due_after_date"] = due_after_date

    # get homeworks
    homeworks = await database.fetch_all(query, query_dict)

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

    # _RETURN
    return {
        "response_code": 200,
        "response": {
            "context": {
                "homeworks": homeworks_formatted,
                "page": page,
            },
            "error": None,
            "message": "Homeworks retrieved successfully",
        },
    }
