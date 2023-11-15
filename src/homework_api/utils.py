from datetime import datetime
from typing import Dict, List, Union

from markupsafe import Markup


def cleanse_api_body(values: Dict[str, any]):
    return {
        key: Markup(value).striptags() if isinstance(value, str) else value
        for key, value in values.items()
    }


def check_valid_dates(dates: List[Union[str, None]]):
    valids = []
    for date in dates:
        if date is None:
            valids.append(True)
            continue

        try:
            datetime.strptime(date, "%Y-%m-%d")
            valids.append(True)
        except ValueError:
            valids.append(False)

    return all(valids)
