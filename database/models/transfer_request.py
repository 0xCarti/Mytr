from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Column, Integer, create_engine, Session, JSON

engine = create_engine("sqlite:///database/database.db")


class transfer_request(SQLModel, table=True):
    id: int = Field(sa_column=Column("id", Integer, unique=True, primary_key=True, autoincrement=True))
    employee_id: str
    location: str
    items_requested: str
    size: int
    dt_created: str
    # date_delivered = Optional[int] = Field(default=None, primary_key=True) # Change default
    archived: Optional[bool] = Field(default=False)


def add_request(employee_id: str = "", location: str = "", items_requested: str = ""):
    with Session(engine) as session:
        request = transfer_request(employee_id=employee_id, location=location, items_requested=items_requested, size=len(items_requested.split(":")) - 1)
        session.add(request)
        session.commit()


def add_requests(requests: list[(str, str, str)]):
    with Session(engine) as session:
        for request in requests:
            rqst = transfer_request(employee_id=request[0], location=request[1], items_requested=request[2], size=len(request[2].split(":")) - 1)
            session.add(rqst)
        session.commit()
