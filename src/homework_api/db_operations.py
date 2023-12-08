from dataclasses import dataclass
from typing import Optional


@dataclass
class getHomeworksCriteria:
    count: int
    offset: int
    assigned_before_date: Optional[str] = None
    assigned_after_date: Optional[str] = None
    due_before_date: Optional[str] = None
    due_after_date: Optional[str] = None


@dataclass
class getHomeworksCountCriteria:
    assigned_before_date: Optional[str] = None
    assigned_after_date: Optional[str] = None
    due_before_date: Optional[str] = None
    due_after_date: Optional[str] = None


async def create_table(db):
    await db.execute(
        """CREATE TABLE IF NOT EXISTS classrooms (
                           ClassroomID INTEGER PRIMARY KEY AUTOINCREMENT,
                           ClassroomSecret TEXT NOT NULL,
                           ClassroomPassword TEXT NOT NULL,
                           ClassroomName TEXT NOT NULL
                           )"""
    )

    await db.execute(
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


async def add_classroom(db, classroom_secret, encrypted_password, classroom_name):
    return await db.execute(
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
            "password": encrypted_password,
            "name": classroom_name,
        },
    )


async def get_classroom_password(db, classroom_secret, encrypted_password):
    return await db.fetch_one(
        """
        SELECT ClassroomID, ClassroomName 
        FROM classrooms 
        WHERE ClassroomSecret = :secret 
        AND ClassroomPassword = :password
        """,
        {"secret": classroom_secret, "password": encrypted_password},
    )


async def get_classroom_no_password(db, classroom_secret):
    return await db.fetch_one(
        """
        SELECT ClassroomID, ClassroomName 
        FROM classrooms 
        WHERE ClassroomSecret = :secret
        """,
        {"secret": classroom_secret},
    )


async def get_teacher(db, classroom_id, subject):
    return await db.fetch_one(
        """
        SELECT Teacher 
        FROM homeworks 
        WHERE ClassroomID = :classroom_id 
        AND Subject = :subject
        AND Teacher IS NOT NULL
        ORDER BY HomeworkID DESC
        LIMIT 1
        """,
        {"classroom_id": classroom_id, "subject": subject},
    )


async def get_homework(db, classroom_id, homework_id):
    return await db.fetch_one(
        """
        SELECT * 
        FROM homeworks 
        WHERE HomeworkID = :homework_id 
        AND ClassroomID = :classroom_id
        """,
        {"homework_id": homework_id, "classroom_id": classroom_id},
    )


async def get_homeworks(
    db,
    classroom_id,
    criteria: getHomeworksCriteria,
):
    conditions = []

    if criteria.assigned_before_date:
        conditions.append("AssignedDate <= :assigned_before_date")

    if criteria.assigned_after_date:
        conditions.append("AssignedDate >= :assigned_after_date")

    if criteria.due_before_date:
        conditions.append("DueDate <= :due_before_date")

    if criteria.due_after_date:
        conditions.append("DueDate >= :due_after_date")

    joined_conditions = " AND ".join(conditions) if conditions else ""

    query = f"""
            SELECT * FROM homeworks 
            WHERE ClassroomID = :classroom_id 
            {'AND' if joined_conditions else ''} {joined_conditions}
            ORDER BY HomeworkID DESC
            LIMIT :count
            OFFSET :offset
            """

    query_dict = {
        "classroom_id": classroom_id,
        "count": criteria.count,
        "offset": criteria.offset,
    }

    for key, value in criteria.__dict__.items():
        if value is not None and key not in ["count", "offset"]:
            query_dict[key] = value

    return await db.fetch_all(query, query_dict)


async def get_homeworks_count(
    db,
    classroom_id,
    criteria: getHomeworksCountCriteria,
):
    conditions = []

    if criteria.assigned_before_date:
        conditions.append("AssignedDate <= :assigned_before_date")

    if criteria.assigned_after_date:
        conditions.append("AssignedDate >= :assigned_after_date")

    if criteria.due_before_date:
        conditions.append("DueDate <= :due_before_date")

    if criteria.due_after_date:
        conditions.append("DueDate >= :due_after_date")

    joined_conditions = " AND ".join(conditions) if conditions else ""

    query = f"""
            SELECT COUNT(HomeworkID) FROM homeworks 
            WHERE ClassroomID = :classroom_id 
            {'AND' if joined_conditions else ''} {joined_conditions}
            """

    query_dict = {
        "classroom_id": classroom_id,
    }

    for key, value in criteria.__dict__.items():
        if value is not None:
            query_dict[key] = value

    return await db.fetch_one(query, query_dict)


async def add_homework(
    db, classroom_id, subject, teacher, title, description, assigned_date, due_date
):
    return await db.execute(
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


async def remove_homework(db, classroom_id, homework_id):
    return await db.execute(
        """
        DELETE FROM homeworks 
        WHERE HomeworkID = :homework_id 
        AND ClassroomID = :classroom_id
        """,
        {"homework_id": homework_id, "classroom_id": classroom_id},
    )


async def get_statistics(
    db, classroom_id, subject, assigned_before_date, assigned_after_date
):
    return await db.fetch_all(
        """
        SELECT AssignedDate FROM homeworks
        WHERE ClassroomID = :classroom_id
        AND Subject = :subject
        AND AssignedDate <= :assigned_before_date
        AND AssignedDate >= :assigned_after_date
        """,
        {
            "classroom_id": classroom_id,
            "subject": subject,
            "assigned_before_date": assigned_before_date,
            "assigned_after_date": assigned_after_date,
        },
    )
