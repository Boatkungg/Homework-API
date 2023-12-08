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


class listHomeworks(BaseModel):
    classroom_secret: str
    count: Union[int, None] = None
    page: Union[int, None] = None
    assigned_before_date: Union[str, None] = None
    assigned_after_date: Union[str, None] = None
    due_before_date: Union[str, None] = None
    due_after_date: Union[str, None] = None


class getHomework(BaseModel):
    classroom_secret: str
    homework_id: str


class statisticsHomework(BaseModel):
    classroom_secret: str
    subject: str
    assigned_before_date: str
    assigned_after_date: str
