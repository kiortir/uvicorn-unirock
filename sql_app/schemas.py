from typing import Optional

from pydantic import BaseModel


class Lead(BaseModel):
    lead_id: int
    material: Optional[str] = None
    specialist: Optional[str] = None
    deal_number: Optional[str] = None
    start_date: Optional[str] = None
    deal_duration: Optional[int] = None
    work_duration: Optional[str] = None
    work_start: Optional[str] = None
    secs: Optional[str] = None

    class Config:
        orm_mode = True


class Token(BaseModel):
    token_type: Optional[str] = None
    token_value: Optional[str] = None

    class Config:
        orm_mode = True
