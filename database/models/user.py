from typing import Optional

from sqlmodel import SQLModel, Field, Column, Integer, create_engine, Session, JSON, VARCHAR


def from_json(json):
    return User(id=json['id'], name=json['name'], pass_hash=json['pass_hash'], email=json['email'], phone=json['phone'], activated=json['activated'], user_type=json['user_type'], transfer_request_history=json['transfer_request_history'])


class User(SQLModel, table=True):
    employee_id: int = Field(sa_column=Column("employee_id", Integer, unique=True, primary_key=True, autoincrement=False, default=0000))
    name: str
    pass_hash: str
    email: Optional[str] = Field(default='')
    phone: Optional[str] = Field(default='')
    activated: Optional[bool] = Field(default=False)
    user_type: Optional[str] = Field(default='user')
    transfer_request_history: Optional[str] = Field(default='')
