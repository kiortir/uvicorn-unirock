from typing import List, Tuple, Optional, Union
import requests
from datetime import datetime, timedelta, date as da


def get_dayoffs() -> Tuple[List[int]]:
    year = datetime.now().year
    day_offs = requests.get(f'http://xmlcalendar.ru/data/ru/{year}/calendar.json').json()['months']
    return tuple([[int(day) for day in month_dict['days'].split(',') if day.find('*') < 0] for month_dict in day_offs])


def is_dayoff(date: datetime, dayoffs: Tuple[List[int]] = get_dayoffs()):
    month_dayoffs = dayoffs[date.month-1]
    # print(date)
    # print(f'{dayoffs}: dayoffs: {month_dayoffs}', f'month: {dayoffs[date.month-1]}', f'date: {date.day}')
    return date.day in month_dayoffs


def true_end(start_date: Union[da, datetime], duration: int, inclusive: bool = True, dayoffs: Tuple[List[int]] = get_dayoffs()) -> Union[da, None]:
    if start_date is None or duration is None:
        return None
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


def true_duration(start_date: da, duration: int, inclusive: bool = True, dayoffs: Tuple[List[int]] = get_dayoffs()) -> int:
    return (start_date - true_end(start_date=start_date, duration=duration, inclusive=inclusive, dayoffs=dayoffs)).days


def deadline(end_date: datetime, work_duration: Optional[int], dayoffs: Tuple[List[int]] = get_dayoffs()):
    if work_duration is None or end_date is None:
        return None
    return true_end(end_date, -work_duration, dayoffs=dayoffs, inclusive=False)


def overtime(end_date: da) -> Union[int, None]:
    if end_date is None:
        return None
    return (datetime.now().date() - end_date).days


if __name__ == '__main__':
    print(overtime(datetime(2021, 8, 1)))
