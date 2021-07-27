from time import time
from typing import List

from sqlalchemy.orm import Session

from . import models


def get_lead(db: Session, lead_id: int):
    return db.query(models.Lead).get(lead_id)  # filter(models.Lead.lead_id == lead_id).first()


def get_token(db: Session, token_type: str) -> str:
    return db.query(models.Tokens).get(token_type).token_value  # filter(models.Tokens.token_type == token_type).first()


def set_tokens(db: Session, tokens: dict):
    tokens['expiration_time'] = tokens['expiration_time'] + time() - 600
    for token_type, token_value in tokens:
        db.execute('UPDATE tokens SET token_value = "%s" WHERE token_type = "%s' % (token_value, token_type))
    db.commit()


def get_ids(db: Session):
    return db.query(models.Lead.lead_id).all()


def delete_lead(db: Session, lead_id: int):
    q = db.query(models.Lead).get(lead_id)
    db.delete(q)
    db.commit()
    return True


def update_lead(db: Session, data: dict):
    q = db.query(models.Lead).filter(models.Lead.lead_id == data['lead_id'])
    q.update(data)
    db.commit()
    return True


def insert_lead(db: Session, data: models.Lead):
    db.add(data)
    db.commit()
    return True


def reset_leads(db: Session, data: List):
    db.query(models.Lead).delete()
    db.bulk_save_objects(data)
    db.commit()
    # db.bulk_save_objects(data)
