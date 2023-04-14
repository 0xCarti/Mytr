from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Column, VARCHAR, create_engine, Session
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

engine = create_engine("sqlite:///database/database.db")


class mobile_notif(SQLModel, table=True):
    number: str = Field(sa_column=Column("number", VARCHAR, unique=True, primary_key=True))
    code: str = Field(sa_column=Column("code", VARCHAR))
    verified: Optional[int] = Field(default=0, index=True)
    dt_verified: Optional[str] = Field(default='', index=True)


def send_notif(a_sid: str, a_token: str, ms_id: str, numbers: list[mobile_notif]):
    for number in numbers:
        client = Client(a_sid, a_token)
        try:
            client.messages.create(messaging_service_sid=ms_id, body=f"TO: {number.number}\n\nTransfer Request Received!\n\nFROM: Bryce's Transfer Service", to=f'+{number.number}')
        except TwilioRestException:
            print(f'Failed to send text to {number.number}')


def verify_number(a_sid: str, a_token: str, ms_id: str, number: str, code: str):
    client = Client(a_sid, a_token)
    try:
        client.messages.create(messaging_service_sid=ms_id, body=f"TO: {number}\n\nCode: {code}\n\nFROM: Bryce's Transfer Service", to=f'+{number}')
    except TwilioRestException:
        print(f'Failed to send code to {number}')


def add_number(number: str):
    with Session(engine) as session:
        item = mobile_notif(number=number)
        session.add(item)
        session.commit()


def add_numbers(numbers: list[str]):
    with Session(engine) as session:
        for number in numbers:
            item = mobile_notif(number=number)
            session.add(item)
        session.commit()
