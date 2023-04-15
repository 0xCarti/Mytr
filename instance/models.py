import random
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from data_handler.pdf_handler import pdf_handler

login = LoginManager()
db = SQLAlchemy()


class UserModel(UserMixin, db.Model):
    __tablename__ = 'users'

    employee_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=False)
    phone = db.Column(db.String(80), unique=False)
    phone_verification_date = db.Column(db.String(80), unique=False)
    name = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(), unique=False)
    user_type = db.Column(db.String(), default='user', unique=False)
    active = db.Column(db.Boolean, default=False, unique=False)
    transfer_request_history = db.Column(db.String(), default='', unique=False)
    last_login = db.Column(db.String(80), unique=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return self.employee_id

    def set_logged_in(self):
        self.last_login = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def set_phone_verified(self):
        self.phone_verification_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def verify_phone(self, a_sid: str, a_token: str, ms_id: str):
        code = str(random.Random().randint(0, 9999))
        client = Client(a_sid, a_token)
        try:
            client.messages.create(messaging_service_sid=ms_id, body=f"TO: {self.phone}\n\nCode: {code}\n\nFROM: Bryce's Transfer Service", to=f'+{self.phone}')
            return code
        except TwilioRestException:
            print(f'Failed to send code to {self.phone}')
            return None


@login.user_loader
def load_user(employee_id: int):
    return UserModel.query.get(employee_id)


class RequestsModel(db.Model):
    __tablename__ = 'requests'

    request_id = db.Column(db.Integer, unique=True, primary_key=True)
    employee_id = db.Column(db.Integer)
    location_id = db.Column(db.Integer)
    requested_items = db.Column(db.String(), default='')
    archived = db.Column(db.Boolean, default=False)
    dt_created = db.Column(db.String(80))

    def get_id(self):
        return self.request_id


class LocationsModel(db.Model):
    __tablename__ = 'locations'

    location_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True)
    transfer_request_history = db.Column(db.String(), default='')

    def get_id(self):
        return self.location_id


class ItemsModel(db.Model):
    __tablename__ = 'items'

    item_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=False)
    transfer_request_history = db.Column(db.String(), default='')

    def get_id(self):
        return self.item_id
