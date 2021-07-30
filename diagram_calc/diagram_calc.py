from . import dates_calc
from sql_app import schemas, models


def calc_data(lead: schemas.ResultLead) -> models.AdditionalLead:
    dayoffs = dates_calc.get_dayoffs()
    end_date = dates_calc.true_end(lead.start_date, lead.deal_duration, True, dayoffs)
    deadline = dates_calc.deadline(end_date, lead.work_duration, dayoffs)
    overtime = dates_calc.overtime(end_date)
    left_till_deadline = dates_calc.overtime(deadline)
    return models.AdditionalLead(lead_id=lead.lead_id, end_date=end_date, deadline=deadline, overtime=overtime,
                                 left_till_deadline=left_till_deadline)


if __name__ == '__main__':
    pass
