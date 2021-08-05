from sql_app import schemas, models
from . import dates_calc
from datetime import date
from typing import List, Tuple, Optional


def calc_data(lead: schemas.ResultLead, dayoffs=dates_calc.get_dayoffs()) -> models.AdditionalLead:
    print(dayoffs)
    end_date = dates_calc.true_end(lead.start_date, lead.deal_duration, True, dayoffs)
    deadline = dates_calc.deadline(end_date, lead.work_duration, dayoffs)
    overtime = dates_calc.overtime(end_date)
    left_till_deadline = dates_calc.overtime(deadline)
    # end_date = deadline = overtime = left_till_deadline = None
    return models.AdditionalLead(lead_id=lead.lead_id, end_date=end_date, deadline=deadline, overtime=overtime,
                                 left_till_deadline=left_till_deadline)


def min_max_date(dates: List[Tuple[date, int]]) -> Tuple[date, Optional[date]]:
    min_date = min([date_tuple[0] for date_tuple in dates if date_tuple[0]])
    max_date = max([dates_calc.true_end(date_tuple[0], date_tuple[1], inclusive=False) for date_tuple in dates if date_tuple[0] and date_tuple[1]])
    return min_date, max_date


if __name__ == '__main__':
    pass
