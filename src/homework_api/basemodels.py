from typing import Union

from pydantic import BaseModel

class newClassroom(BaseModel):
    classroom_name: str
    classroom_password: str


class addHomework(BaseModel):
    classroom_secret: str
    classroom_password: str
    subject: str
    teacher: Union[str, None] = None
    title: str
    description: Union[str, None] = None
    assigned_date: Union[str, None] = None
    due_date: str


class removeHomework(BaseModel):
    classroom_secret: str
    classroom_password: str
    homework_id: int


class getHomeworks(BaseModel):
    classroom_secret: str
    classroom_password: str
    count: int = 10
