from typing import List
from datetime import datetime
from markupsafe import Markup

def normalize_strings(values: List[str]):
    return [Markup(value).striptags() for value in values]

def check_valid_date(date: str):
    try:
        datetime.strptime(date, "%d-%m-%Y")
        return True
    except ValueError:
        return False
