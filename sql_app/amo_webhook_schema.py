from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class Field0(BaseModel):
    id: int
    name: str
    status_id: int
    old_status_id: int
    price: str
    responsible_user_id: str
    last_modified: int
    modified_user_id: int
    created_user_id: int
    date_create: int
    pipeline_id: int
    tags: dict
    account_id: int
    custom_fields: Optional[dict] = None
    created_at: int
    updated_at: int


class Update(BaseModel):
    field_0: Field0 = Field(..., alias='0')


class Delete(BaseModel):
    field_0: Field0 = Field(..., alias='0')


class Leads(BaseModel):
    update: Optional[Update] = None
    delete: Optional[Delete] = None


class _Links(BaseModel):
    self: str


class Account(BaseModel):
    subdomain: str
    id: str
    _links: _Links


class Model(BaseModel):
    leads: Leads
    account: Account
