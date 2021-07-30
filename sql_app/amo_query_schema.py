# from __future__ import annotations

from typing import Any, List, Optional, Union

from pydantic import BaseModel


class Value(BaseModel):
    value: Union[bool, int, str]
    enum_id: Optional[int] = None
    enum_code: Optional[Any] = None


class CustomFieldsValue(BaseModel):
    field_id: int
    field_name: str
    field_code: Any
    field_type: str
    values: List[Value]


class Self(BaseModel):
    href: str


class _Links(BaseModel):
    self: Self


class Self1(BaseModel):
    href: str


class _Links1(BaseModel):
    self: Self1


class Company(BaseModel):
    id: int
    _links: _Links1


class _Embedded(BaseModel):
    tags: List
    companies: List[Company]


class Model(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    price: Optional[int] = None
    responsible_user_id: Optional[int] = None
    group_id: Optional[int] = None
    status_id: Optional[int] = None
    pipeline_id: Optional[int] = None
    loss_reason_id: Optional[Any] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
    closed_at: Optional[Any] = None
    closest_task_at: Optional[Any] = None
    is_deleted: Optional[bool] = None
    custom_fields_values: Optional[List[CustomFieldsValue]] = None
    score: Optional[Any] = None
    account_id: Optional[int] = None
    _links: Optional[_Links] = None
    _embedded: Optional[_Embedded] = None
