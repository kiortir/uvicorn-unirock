from time import time
from typing import List

from sqlalchemy.orm import Session

from . import models


def get_lead(db: Session, lead_id: int):
    return db.query(models.Lead).get(lead_id)


def get_additional_lead(db: Session, lead_id: int):
    return db.query(models.AdditionalLead).get(lead_id)


def get_token(db: Session, token_type: str) -> str:
    return db.query(models.Tokens).get(token_type).token_value


def set_tokens(db: Session, tokens: dict):
    del tokens['token_type']
    tokens['expiration_time'] = tokens['expires_in'] + time() - 600
    del tokens['expires_in']
    for token_type, token_value in tokens.items():
        db.execute("UPDATE tokens SET token_value = '%s' WHERE token_type = '%s'" % (token_value, token_type))
    db.commit()


def get_ids(db: Session):
    return db.query(models.Lead.lead_id).all()


def delete_lead(db: Session, lead_id: int):
    q = db.query(models.Lead).get(lead_id)
    db.delete(q)
    db.commit()
    return True


def update_additional_values(db: Session, data: models.AdditionalLead):
    q = db.query(models.Lead).filter(models.AdditionalLead.lead_id == data.lead_id)
    q.update(data)
    db.commit()


def update_lead(db: Session, data: dict):
    q = db.query(models.Lead).filter(models.Lead.lead_id == data['lead_id'])
    q.update(data)
    db.commit()
    return True


def insert_lead(db: Session, data: models.Lead):
    db.add(data)
    db.commit()
    return True


def insert_additional_info(db: Session, data: models.Lead):
    db.add(data)
    db.commit()


def show_leads(db: Session) -> List[models.Lead]:
    return db.query(models.Lead).all()


def show_add_leads(db: Session):
    return db.query(models.AdditionalLead).all()


def join_show(db: Session):
    return db.query(models.Lead, models.AdditionalLead).all()


def reset_leads(db: Session, data: List):
    db.query(models.Lead).delete()
    db.bulk_save_objects(data)
    db.commit()


def reset_addition_values(db: Session, data: List[models.AdditionalLead]):
    db.query(models.AdditionalLead).delete()
    db.bulk_save_objects(data)
    db.commit()


def create_lead_props(db: Session):
    db.execute("CREATE TABLE lead_props (lead_id INTEGER, deadline date)")
