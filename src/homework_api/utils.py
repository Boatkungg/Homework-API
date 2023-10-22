from typing import List, Union
from datetime import datetime
from markupsafe import Markup


def normalize_strings(values: List[Union[str, None]]):
    return [
        Markup(value).striptags() if value is not None else None for value in values
    ]


def check_valid_date(date: Union[str, None]):
    if date is None:
        return True

    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False
