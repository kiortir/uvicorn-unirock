from sqlalchemy import Column, Integer, String

from .database import Base


class Lead(Base):
    __tablename__ = "leads"

    lead_id = Column("lead_id", Integer, primary_key=True)
    material = Column("material", String)
    specialist = Column("specialist", String)
    deal_number = Column("deal_number", String)
    start_date = Column("start_date", String)
    deal_duration = Column("deal_duration", String)
    work_duration = Column("work_duration", String)
    work_start = Column("work_start", String)
    secs = Column("secs", String)


class Tokens(Base):
    __tablename__ = "tokens"

    token_type = Column("token_type", String, primary_key=True)
    token_value = Column("token_value", String)
    #
    # def update(self, **kwargs):
    #     for key, value in kwargs.items():
    #         if hasattr(self, key):
    #             setattr(self, key, value)
