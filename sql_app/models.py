from sqlalchemy import Column, Integer, String, Date

from .database import Base


class Lead(Base):
    __tablename__ = "leads"

    lead_id = Column("lead_id", Integer, primary_key=True)
    material = Column("material", String)
    specialist = Column("specialist", String)
    deal_number = Column("deal_number", String)
    start_date = Column("start_date", Date)
    deal_duration = Column("deal_duration", Integer)
    work_duration = Column("work_duration", Integer)
    work_start = Column("work_start", Date)
    secs = Column("secs", Date)


class AdditionalLead(Base):
    __tablename__ = 'leads_info'

    lead_id = Column("lead_id", Integer, primary_key=True)
    deadline = Column("deadline", Date)
    end_date = Column("end_date", Date)
    overtime = Column("overtime", Integer)
    left_till_deadline = Column("left_till_deadline", Integer)


class Tokens(Base):
    __tablename__ = "tokens"

    token_type = Column("token_type", String, primary_key=True)
    token_value = Column("token_value", String)
