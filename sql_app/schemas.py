from typing import Optional, Union
from datetime import datetime
from pydantic import BaseModel


class ResultLead(BaseModel):
    lead_id: int
    material: Optional[str] = None
    specialist: Optional[str] = None
    deal_number: Optional[str] = None
    start_date: Optional[Union[None, datetime]] = None
    deal_duration: Optional[int] = None
    work_duration: Optional[Union[None, int]] = None
    work_start: Optional[Union[None, datetime]] = None

    class Config:
        orm_mode = True


class AdditionalLead(BaseModel):
    lead_id: int
    deadline: datetime
    end_date: datetime
    overtime: int
    left_till_deadline: int


class Token(BaseModel):
    token_type: Optional[str] = None
    token_value: Optional[str] = None

    class Config:
        orm_mode = True
