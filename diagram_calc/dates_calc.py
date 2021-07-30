from typing import List, Tuple, Optional
import requests
from datetime import datetime, timedelta


def get_dayoffs() -> Tuple[List[int]]:
    year = datetime.now().year
    day_offs = requests.get(f'http://xmlcalendar.ru/data/ru/{year}/calendar.json').json()['months']
    return tuple([[int(day) for day in month_dict['days'].split(',') if day.find('*') < 0] for month_dict in day_offs])


def is_dayoff(date: datetime, dayoffs: Tuple[List[int]] = get_dayoffs()):
    month_dayoffs = dayoffs[date.month-1]
    return date.day in month_dayoffs


def true_end(start_date: datetime, duration: int, inclusive: bool = True, dayoffs: Tuple[List[int]] = get_dayoffs()) -> datetime:
    if duration < 0:
        delta = -1
        duration = duration*-1
    else:
        delta = 1
    if inclusive and not is_dayoff(start_date):
        duration -= inclusive
    while duration > 0:
        start_date += timedelta(days=delta)
        if is_dayoff(start_date, dayoffs):
            continue
        duration -= 1
    return start_date


def true_duration(start_date: datetime, duration: int, inclusive: bool = True, dayoffs: Tuple[List[int]] = get_dayoffs()) -> int:
    return (start_date - true_end(start_date=start_date, duration=duration, inclusive=inclusive, dayoffs=dayoffs)).days


def deadline(end_date: datetime, work_duration: Optional[int], dayoffs: Tuple[List[int]] = get_dayoffs()):
    if work_duration is None:
        return None
    return true_end(end_date, -work_duration, dayoffs=dayoffs, inclusive=False)


def overtime(end_date: datetime) -> int:
    return (datetime.now().date() - end_date).days


if __name__ == '__main__':
    print(deadline(datetime(2021, 8, 2), 10, dayoffs=get_dayoffs()))
