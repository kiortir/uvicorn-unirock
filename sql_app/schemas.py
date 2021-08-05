from typing import Optional, Union
from datetime import datetime, date, timedelta
from pydantic import BaseModel


class ResultLead(BaseModel):
    lead_id: int
    material: Optional[str] = None
    specialist: Optional[str] = None
    deal_number: Optional[str] = None
    start_date: Optional[Union[date, str, None]] = None
    deal_duration: Optional[Union[int, str, None]] = None
    work_duration: Optional[Union[int, str, None]] = None
    work_start: Optional[Union[date, str, None]] = None

    class Config:
        orm_mode = True


class AdditionalLead(BaseModel):
    lead_id: Optional[int] = None
    deadline: Optional[date] = None
    end_date: Optional[date] = None
    overtime: Optional[int] = None
    left_till_deadline: Optional[int] = None

    class Config:
        orm_mode = True


class Lead(BaseModel):
    main_info: ResultLead
    calculated_info: AdditionalLead


class Token(BaseModel):
    token_type: Optional[str] = None
    token_value: Optional[str] = None

    class Config:
        orm_mode = True
