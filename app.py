import json
import secrets
from datetime import datetime

import flask
from flask import Flask, redirect, render_template, url_for
from flask_login import login_required, current_user, login_user, logout_user

from data_handler.pdf_handler import pdf_handler
from instance.models import db, login, UserModel, ItemsModel, LocationsModel, RequestsModel

verification_codes = {}
app = Flask(__name__)
app.secret_key = secrets.token_urlsafe(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()
login.init_app(app)
login.login_view = 'login'


@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    stock_items = ItemsModel.query.all()
    stock_locations = LocationsModel.query.all()
    return render_template('authenticated/basic/requests/create_request.html', stock_items=stock_items, stock_locations=stock_locations, current_user=current_user)


@app.route('/requests/', methods=['POST', 'GET'])
@login_required
def requests():
    if flask.request.method == 'POST':
        # get all the data from the transfer
        employee_id = flask.request.json['employee_id']
        location = flask.request.json['location']
        requested_items = flask.request.json['items_requested']
        # create the transfer and add it to the db
        location = LocationsModel.query.filter_by(name=location).first()
        transfer = RequestsModel(employee_id=employee_id, location_id=location.location_id, requested_items=json.dumps(requested_items), dt_created=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        db.session.add(transfer)
        # update location with transfer ID
        if location:
            history = location.transfer_request_history
            history = history + f'{transfer.request_id}:'
            location.transfer_request_history = history
            db.session.add(location)
        # update items with transfer id
        for item_name in requested_items:
            item = ItemsModel.query.filter_by(name=item_name).first()
            if item:
                history = item.transfer_request_history
                history = history + f'{transfer.request_id}:'
                item.transfer_request_history = history
                db.session.add(item)
        db.session.commit()
        # send out the mobile notif
        # statement = select(mn.mobile_notif)
        # notif_numbers = session.exec(statement).fetchall()
        # mn.send_notif(config['TWILIO_ID'], config['TWILIO_TOKEN'], config['TWILIO_MSG_SID'], notif_numbers)
        return redirect('/home')
    elif flask.request.method == 'GET':
        locations = LocationsModel.query.all()
        transfer_requests = RequestsModel.query.all()
        return render_template('authenticated/basic/requests/transfer-requests.html', transfer_requests=transfer_requests, locations=locations)


@app.route('/request/<request_id>', methods=['POST', 'GET'])
@login_required
def request(request_id: int):
    if flask.request.method == 'POST' and current_user.user_type == 'admin':
        request = RequestsModel.query.filter_by(request_id=request_id).first()
        if request:
            request.archived = True
            db.session.add(request)
            db.session.commit()
            return redirect('/requests/')
        else:
            return 'fail'
    elif flask.request.method == 'GET':
        transfer_request = RequestsModel.query.filter_by(request_id=request_id).first()
        requested_items = json.loads(transfer_request.requested_items)
        return render_template('authenticated/basic/requests/transfer-request.html', transfer_request=transfer_request, requested_items=requested_items)


@app.route('/merge/<ids>', methods=['GET'])
@login_required
def merge(request_ids: str):
    request_ids = request_ids.removesuffix(":").split(":")
    all_items = {}
    na_amounts = []
    for request_id in request_ids:
        transfer_request = RequestsModel.query.filter_by(request_id=int(request_id)).first()
        requested_items = json.loads(transfer_request.items_requested)
        for item in requested_items:
            if requested_items[item] == 'N/A':
                na_amounts.append(item)
                continue
            if item in all_items:
                all_items[item] = str(int(all_items[item]) + int(requested_items[item]))
            else:
                all_items[item] = '0'
                all_items[item] = str(int(all_items[item]) + int(requested_items[item]))
    for item in na_amounts:
        if item not in all_items:
            all_items[item] = '0'
        all_items[item] = f'{all_items[item]}+'
    return render_template('authenticated/basic/requests/merged-request.html', requested_items=all_items)


@app.route('/items', methods=['POST', 'GET'])
@login_required
def items():
    mode = flask.request.args.get('mode')
    if mode == 'add' and current_user.user_type == 'admin':
        name = flask.request.args.get('name')
        stock_item = ItemsModel(name=name)
        db.session.add(stock_item)
        db.session.commit()
    elif mode == 'delete' and current_user.user_type == 'admin':
        item_ids = flask.request.args.get('ids').removesuffix(":").split(':')
        for item_id in item_ids:
            item = ItemsModel.query.filter_by(item_id=item_id).first()
            db.session.delete(item)
        db.session.commit()
    stock_items = ItemsModel.query.all()
    return render_template('authenticated/basic/items/stock_items.html', stock_items=stock_items)


@app.route('/item/<item_id>', methods=['POST', 'GET'])
@login_required
def item(item_id: int):
    if flask.request.method == 'POST':
        pass
    elif flask.request.method == 'GET':
        item = LocationsModel.query.filter_by(item_id=item_id).first
        if item:
            request_id_history = item.transfer_request_history.removesuffix(':').split(':')
            request_history = []
            for request_id in request_id_history:
                request = RequestsModel.query.filter_by(request_id=request_id).first()
                if request:
                    request_history.append(request)
            return render_template('authenticated/basic/locations/view-location.html', item=item, history=request_history)
    return render_template('public/404.html')


@app.route('/locations', methods=['POST', 'GET'])
@login_required
def locations():
    if flask.request.method == 'POST':
        mode = flask.request.args.get('mode')
        if mode == 'add' and current_user.user_type == 'admin':
            name = flask.request.json['name']
            stock_location = LocationsModel(name=name)
            db.session.add(stock_location)
            db.session.commit()
            return redirect('/locations')
        elif mode == 'delete' and current_user.user_type == 'admin':
            location_ids = flask.request.args.get('ids').removesuffix(":").split(':')
            for location_id in location_ids:
                location = LocationsModel.query.filter_by(location_id=location_id).first()
                db.session.delete(location)
            db.session.commit()
    elif flask.request.method == 'GET':
        stock_locations = LocationsModel.query.all()
        return render_template('authenticated/basic/locations/stock-locations.html', stock_locations=stock_locations)


@app.route('/location/<location_id>', methods=['POST', 'GET'])
@login_required
def location(location_id: int):
    if flask.request.method == 'POST' and current_user.user_type == 'admin':
        pass # delete the location?
    elif flask.request.method == 'GET':
        location = LocationsModel.query.filter_by(location_id=location_id).first()
        if location:
            transfers = RequestsModel.query.filter_by(location_id=location.location_id)
            return render_template('authenticated/basic/locations/view-location.html', location=location, history=transfers)
    return render_template('public/404.html')


@app.route('/users', methods=['POST', 'GET'])
@login_required
def users():
    if flask.request.method == 'POST' and current_user.user_type == 'admin':
        employee_id = flask.request.json['employee_id']
        user = UserModel.query.filter_by(employee_id=int(employee_id)).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return redirect('/users')
        else:
            return 'fail'  # make the page display a note for the user, so they know tiw as a fail
    elif flask.request.method == 'GET' and current_user.user_type == 'admin':
        users = UserModel.query.all()
        return render_template('authenticated/basic/user/users.html', users=users)


@app.route('/profile/<employee_id>', methods=['POST', 'GET'])
@login_required
def profile(employee_id):
    if flask.request.method == 'POST':
        if current_user.user_type == 'admin' or current_user.get_id() == int(employee_id):
            name = flask.request.json['name']
            email = flask.request.json['email']
            phone = flask.request.json['phone']
            password = flask.request.json['password']
            user_type = flask.request.json['user_type']
            activated = bool(flask.request.json['activated'])
            user = UserModel.query.filter_by(employee_id=employee_id).first()
            if user:
                user.name = name
                user.email = email
                user.phone = phone
                user.user_type = user_type
                user.active = activated
                if password != '':
                    user.set_password(password)
                db.session.add(user)
                db.session.commit()
                return redirect(f'/profile/{employee_id}')
        return 'fail'  # make the page display a note for the user, so they know tiw as a fail
    elif flask.request.method == 'GET':
        if current_user.user_type == 'admin' or current_user.get_id() == int(employee_id):
            profile_user = UserModel.query.filter_by(employee_id=employee_id).first()
            if profile_user:
                return render_template('authenticated/basic/user/profile.html', profile_user=profile_user, session_user=current_user)
        return render_template('public/404.html')


@app.route('/database', methods=['POST', 'GET'])
def database():
    mode = flask.request.args.get('func')
    if mode == 'init-items':
        pdfh = pdf_handler('data_handler/stock_items_summary.pdf')
        items = pdfh.import_venue_stock_items()
        for item in items:
            if not item.startswith('Delete'):
                item = ItemsModel(name=item)
                db.session.add(item)
        try:
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
        return redirect(url_for('admin'))
    if mode == 'init-locs':
        with open("data_handler/locations_data.txt") as file:
            lines = file.readlines()
            lines = [x.strip() for x in lines]
            for line in lines:
                location = LocationsModel(name=line.split(':')[0])
                db.session.add(location)
            try:
                db.session.commit()
            except:
                db.session.rollback()
        return redirect(url_for('admin'))
    if mode == 'init-dev-users':
        print('init dev')
        user = UserModel(employee_id=1061, name='Bryce Cotton', user_type='admin', active=1)
        user.set_password('Snotsuh1')
        db.session.add(user)
        db.session.commit()
        redirect('/login')


@app.route('/admin', methods=['POST', 'GET'])
@login_required
def admin():
    if current_user.user_type == 'admin':
        return render_template('authenticated/admin/admin.html')
    else:
        return render_template('public/404.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if flask.request.method == 'POST':
        employee_id = flask.request.json['employee_id']
        name = flask.request.json['name']
        password = flask.request.json['password']
        user = UserModel.query.filter_by(employee_id=employee_id).first()
        if user:
            return 'Employee ID already Present'
        user = UserModel(employee_id=employee_id, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    else:
        return render_template('public/signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(f'/profile/{current_user.employee_id}')

    if flask.request.method == 'POST':
        employee_id = flask.request.json['employee_id']
        user = UserModel.query.filter_by(employee_id=int(employee_id)).first()
        if user and user.active and user.check_password(flask.request.json['password']):
            login_user(user)
            return redirect(f'/profile/{employee_id}')
        else:
            return 'Invalid User or Credentials.'  # make the page display a note for the user, so they know tiw as a fail

    return render_template('public/login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')


@app.template_filter('inverse')
def inverse(obj):
    return not (bool(obj))


@app.template_filter('is_hidden')
def is_hidden(obj):
    if obj.user_type == 'user':
        return 'hidden'
    else:
        return ''

@app.template_filter('get_location_name')
def get_location_name(location_id):
    location = LocationsModel.query.filter_by(location_id=location_id).first()
    if location:
        return location.name
    else:
        return ''


if __name__ == '__main__':
    # app.run(host='0.0.0.0', port=8000)
    app.run(host='0.0.0.0', port=5000, debug=True)
