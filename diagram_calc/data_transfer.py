from sqlalchemy.orm import Session
from sql_app import models, crud
from typing import List
from .body import calc_data


def commit_additional_fields(db: Session, data: List[models.Lead]):
    new_data = list(map(calc_data, data))



