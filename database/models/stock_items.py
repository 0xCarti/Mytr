from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlmodel import create_engine, Session, SQLModel, Field, Column, Integer, VARCHAR

from data_handler.pdf_handler import pdf_handler

engine = create_engine("sqlite:///database/database.db")


class stock_items(SQLModel, table=True):
    si_code: str = Field(sa_column=Column("id", Integer, unique=True, primary_key=True, autoincrement=True))
    name: str = Field(sa_column=Column("name", VARCHAR, unique=True))
    transfer_request_history: Optional[str] = Field(default='')


def import_all_stock_items():
    pdfh = pdf_handler('data_handler/stock_items_summary.pdf')
    items = pdfh.import_venue_stock_items()
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        for stk_item in items:
            if not stk_item.startswith('Delete'):
                item = stock_items(name=stk_item)
                session.add(item)
                try:
                    session.commit()
                except IntegrityError:
                    session.rollback()


def add_stock_item(name: str):
    with Session(engine) as session:
        item = stock_items(name=name)
        session.add(item)
        session.commit()


def add_stock_items(names: list[str]):
    with Session(engine) as session:
        for name in names:
            item = stock_items(name=name)
            session.add(item)
        session.commit()
