from flask import Flask,render_template,request,url_for,redirect
from flask import current_app as app
from models import *
from datetime import datetime
import pytz
from sqlalchemy import func,desc  
import matplotlib.pyplot as plt
plt.switch_backend('agg') 
from sqlalchemy import func, case


############################################ ROUTE FUNCTIONALITIES COMMON FOR ADMIN/USER ###########################################


# Route for Landing Page
@app.route('/', methods =['GET', 'POST'])
def landing_page():
    return render_template('landing_page.html')





#Route for creating login to admin , customer reddirect.
@app.route('/login' , methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        print(email)

        user = User.query.filter_by(email = email).first()

        if not user:
            print('No registered user found')
            return render_template('login.html', error="User not found")
        if user.password == password and user.role == 1:
            print('Customer Login Successful')
            return redirect(url_for('user_dashboard', user = user.name))
        elif user.password == password and user.role == 0:
            print('Admin Login Successful')
            return redirect(url_for('admin_dashboard'))
        else:
            print('Password Incorrect')
    return render_template('login.html')





# Creating signup page for customer
@app.route('/signup' , methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        print(email)
        user = User(email = email, password = password, name = name, address = address, pincode = int(pincode), role = 1)
        db.session.add(user)
        db.session.commit()
        print('User created successfully')
        return redirect(url_for('login'))
    return render_template('signup.html')





############################################ ROUTE FUNCTIONALITIES FOR ADMIN ###########################################


# Route for Admin Dashboard
@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    recent_bookings = ReserveParkingSpot.query.all()
    if request.method == 'POST':
        pass
    parking_lot = ParkingLot.query.all()
    alert_message = request.args.get('alert_message')
    return render_template('admin_dashboard.html',parkinglot=parking_lot, recent_bookings= recent_bookings, alert_message= alert_message)





# Route for Add Parking Lot
@app.route('/add', methods = ['GET', 'POST'])
def add_parking_lot():
    if request.method =='POST':
        location = request.form.get('location')
        pincode = request.form.get('pincode')
        price = request.form.get('price')
        available_spots = request.form.get('available_spots')
        new_parking_lot = ParkingLot(location = location, pin_code = int(pincode), price = int(price), available_spots = int(available_spots))
        db.session.add(new_parking_lot)
        db.session.commit()
        lot_id = ParkingLot.query.filter_by(location = location).first().id
        for i in range(int(available_spots)):
            spot = ParkingSpot(lot_id = lot_id, status = 'Available')
            db.session.add(spot)
        db.session.commit()
    return render_template('add_parking_lot.html')





# Route for delete Parking Lot
@app.route('/delete/<id>', methods=['GET', 'POST'])
def delete_parking_lot(id):
    parking_lot = ParkingLot.query.filter_by(id=id).first()
    occupied_spot = ParkingSpot.query.filter_by(lot_id = id, status = 'Occupied').first()
    if occupied_spot:
        return redirect(url_for('admin_dashboard', alert_message = "Some spots are occupied, you can't delete it"))
    if parking_lot:
        db.session.delete(parking_lot)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))





# Route for edit Parking Lot
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_parking_lot(id):
    parking_lot = ParkingLot.query.filter_by(id=id).first()
    if request.method == 'POST':
        location = request.form.get('location')
        pincode = request.form.get('pincode')
        price = request.form.get('price')
        available_spots = request.form.get('available_spots')
        if parking_lot:
            parking_lot.location = location
            parking_lot.pin_code = int(pincode)
            parking_lot.price = int(price)
            parking_lot.available_spots = int(available_spots)
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
    return render_template('edit_parking_lot.html', lot = parking_lot)





#Route for viewing spot
@app.route('/view/<int:lot_id>')
def view_spots_status(lot_id):
    spots = ParkingSpot.query.filter_by(lot_id = lot_id).all()
    return render_template('view_spots.html', spots=spots)





# Route to see all the users
@app.route('/users', methods = ['GET', 'POST'])
def all_users():
    users = User.query.filter_by(role = 1).all()
    return render_template('admin_user.html', users = users)





# Route to search users on admin dashboard
@app.route('/search', methods=['GET'])
def search():
    category = request.args.get('category')
    query = request.args.get('query')
    results = []
    if category and query:
        query = query.strip()
        if category == 'user':
            results = User.query.filter(
                (User.name == query) |
                (User.email == query) |
                (User.address == query)
            ).all()
        elif category == 'parking':
            if query.isdigit():
                pin_code = int(query)
                results = ParkingLot.query.filter_by(pin_code=pin_code).all()
            else:
                results = ParkingLot.query.filter_by(location=query).all()
    return render_template('admin_search.html', category=category, query=query, results=results)





# Route for Admin Summary
@app.route('/summary')
def show_admin_summary():
    lots = ParkingLot.query.all()
    chart_data = []
    for lot in lots:
        spots = lot.spot or []  # safe fallback
        total = len(spots)
        occupied = sum(1 for s in spots if s.status in ['Occupied', 'O'])
        available = sum(1 for s in spots if s.status in ['Available', 'A'])

        chart_data.append({
            "location": lot.location or "Unknown",
            "occupied": occupied,
            "available": available,
            "total": total
        })
    return render_template("admin_summary.html", chart_data= chart_data)





# Route to see Occupied Spots
@app.route("/occupied_spots")
def occupied_spots():
    reservations = ReserveParkingSpot.query.filter_by(leaving_timestamp=None).all()
    occupied_reservations = [r for r in reservations if r.spot.status == 'Occupied']
    return render_template("occupied_parking_spot_details.html", occupied_spots=occupied_reservations)










############################################ ROUTE FUNCTIONALITIES FOR USER ###########################################


# Route for User Dashboard
@app.route('/user_dashboard/<user>', methods = ['GET', 'POST'])
def user_dashboard(user):
    customer = User.query.filter_by(name = user).first()
    active_booking = ReserveParkingSpot.query.filter_by(user_id = customer.id, status ='Occupied').all()
    booking_history = ReserveParkingSpot.query.filter_by(user_id = customer.id, status = 'Closed').all()
    if request.method == 'POST':
        pass
    return render_template('user_dashboard.html', user = user, active_booking = active_booking, booking_history= booking_history)





# Route for User Search
@app.route('/user_search/<user>', methods = ['GET', 'POST'])
def user_search(user):
    if request.method == 'POST':
        query = request.form.get('query')
        print(query)
        results = ParkingLot.query.filter(
            (ParkingLot.location == query) | (ParkingLot.pin_code == query)
        ).all()
        customer = User.query.filter_by(name=user).first()
        active_booking = ReserveParkingSpot.query.filter_by(user_id=customer.id, status='Occupied').all()
        booking_history = ReserveParkingSpot.query.filter_by(user_id=customer.id, status='Closed').all()
        return render_template('user_dashboard.html', user=user, active_booking=active_booking, booking_history=booking_history, search_results=results, query=query)
    return redirect(url_for('user_dashboard', user=user))





#Route for booking parking lot
@app.route('/<user>/book/<lot_id>', methods = ['GET', 'POST'])
def book_parkingspot(user, lot_id):
    lot = ParkingLot.query.filter_by(id = lot_id).first()
    available_spots = ParkingSpot.query.filter_by(lot_id = lot_id, status = 'Available').all()
    customer = User.query.filter_by(name = user).first()
    if request.method == 'POST':
        spot_id = request.form.get('spot_id')
        vehicle_number = request.form.get('vehicle_number')
        new_record = ReserveParkingSpot(spot_id = spot_id, user_id = customer.id, parking_timestamp = datetime.utcnow(), vehicle_number = vehicle_number, status = 'Occupied')
        booked_spot = ParkingSpot.query.filter_by(id = spot_id).first()
        booked_spot.status = 'Occupied'
        lot.available_spots = lot.available_spots - 1
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('user_dashboard', user = user))
    return render_template('book_parkinglot.html', user = user , lot = lot, available_spots = available_spots)





# Route for Releasing Parking Spot
@app.route('/<username>/end_booking/<int:active_booking_id>', methods=['GET', 'POST'])
def end_booking(username, active_booking_id):
    customer = User.query.filter_by(name=username).first()
    history = ReserveParkingSpot.query.filter_by(id=active_booking_id).first()
    history.leaving_timestamp = datetime.utcnow()
    total_time = (history.leaving_timestamp - history.parking_timestamp).total_seconds()
    spot_id = history.spot_id
    spot = ParkingSpot.query.filter_by(id=spot_id).first()
    lot_id = spot.lot_id
    lot = ParkingLot.query.filter_by(id=lot_id).first()
    price_per_hour = lot.price
    total_hours = total_time / 3600
    cost = round(total_hours * price_per_hour, 2)
    history.parking_cost = cost
    spot.status = 'Available'
    lot.available_spots = lot.available_spots + 1
    history.status = 'Closed'
    db.session.commit()
    return redirect(url_for('user_dashboard', user = username ))





# Route for edit profile
@app.route('/edit_profile/<user>', methods = ['GET', 'POST'])
def edit_profile(user):
    customer = User.query.filter_by(name=user).first()
    print (customer)
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        address = request.form.get('address')
        pincode = request.form.get('pincode')
        customer.email = email
        customer.password = password
        customer.name = name
        customer.address = address
        customer.pincode = int(pincode)
        db.session.commit()
        return redirect(url_for('user_dashboard', user = customer.name))
    return render_template('user_edit_profile.html', customer = customer)





# Route for User Summary
@app.route('/user_summary/<user>')
def show_user_summary(user):
    user_bookings = (
        db.session.query(
            User.id,
            User.name,
            func.sum(
                case(
                    (ReserveParkingSpot.status == 'Occupied', 1),
                    else_=0
                )
            ).label("occupied_count"),
            func.sum(
                case(
                    (ReserveParkingSpot.status == 'Closed', 1),
                    else_=0
                )
            ).label("closed_count"),
        )
        .join(ReserveParkingSpot, ReserveParkingSpot.user_id == User.id)
        .group_by(User.id, User.name)
        .all()
    )

    chart_data = []
    for row in user_bookings:
        chart_data.append({
            "user_name": row.name,
            "occupied": int(row.occupied_count),
            "closed": int(row.closed_count)
        })
    return render_template("user_summary.html", user = user, chart_data = chart_data)