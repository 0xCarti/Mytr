import json
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
    enable_mobile_notifications = db.Column(db.Boolean, default=False, unique=False)
    name = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.String(), unique=False)
    user_type = db.Column(db.String(), default='user', unique=False)
    active = db.Column(db.Boolean, default=False, unique=False)
    transfer_request_history = db.Column(db.String(), default='', unique=False)
    last_login = db.Column(db.String(80), unique=False)

    def set_password(self, password, use_hash=True):
        if use_hash:
            self.password_hash = generate_password_hash(password)
        else:
            self.password_hash = password

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

    def to_json(self):
        return json.dumps({"employee_id": self.employee_id, "name": self.name, "hash": self.password_hash, "user_type": self.user_type})


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

    def to_json(self):
        return json.dumps({"location_id": self.location_id, "name": self.name, "transfer_request_history": ''})


class ItemsModel(db.Model):
    __tablename__ = 'items'

    item_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True)
    transfer_request_history = db.Column(db.String(), default='')
    transfer_unit = db.Column(db.String(80), default='Each')

    def get_id(self):
        return self.item_id

    def to_json(self):
        return json.dumps({"item_id": self.item_id, "name": self.name, "transfer_request_history": '', 'transfer_unit': self.transfer_unit})


class TransferUnitModel(db.Model):
    __tablename__ = 'transfer_units'

    unit_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True)

    def get_id(self):
        return self.unit_id

    def to_json(self):
        return json.dumps({"unit_id": self.unit_id, "name": self.name})


class TrackersModel(db.Model):
    __tablename__ = 'trackers'

    tracker_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer)
    name = db.Column(db.String(80), unique=False)
    quantity = db.Column(db.Integer)
    date_received = db.Column(db.String(80))
    expiry_date = db.Column(db.String(80))

    def get_id(self):
        return self.tracker_id

    def to_json(self):
        return json.dumps({"tracker_id": self.tracker_id, "employee_id": self.employee_id, 'name': self.name, 'quantity': self.quantity, 'date_received': self.date_received, 'expiry_date': self.expiry_date})


class FeedbackModel(db.Model):
    __tablename__ = 'inventories'

    feedback_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, default=0)
    subject = db.Column(db.String())
    message = db.Column(db.String(), default='')
    date_created = db.Column(db.String(80))

    def get_id(self):
        return self.feedback_id

    def to_json(self):
        return json.dumps({"feedback_id": self.feedback_id, "employee_id": self.employee_id, 'subject': self.subject, 'message': self.message, 'date_created': self.date_created})
