from typing import Optional

from sqlmodel import create_engine, Session, SQLModel, Field, Column, Integer, VARCHAR

engine = create_engine("sqlite:///database/database.db")


class stock_locations(SQLModel, table=True):
    si_code: str = Field(sa_column=Column("si_code", Integer, unique=True, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column("name", VARCHAR, unique=True))
    transfer_request_history: Optional[str] = Field(default='')


def import_all_locations():
    with open("data_handler/locations_data.txt") as file:
        lines = file.readlines()
        lines = [x.strip() for x in lines]
    with Session(engine) as session:
        for line in lines:
            location = stock_locations(name=line.split(':')[0])
            session.add(location)
        session.commit()


def add_stock_location(name: str):
    with Session(engine) as session:
        location = stock_locations(name=name)
        session.add(location)
        session.commit()


def add_stock_locations(names: list[str]):
    with Session(engine) as session:
        for name in names:
            location = stock_locations(name=name)
            session.add(location)
        session.commit()
