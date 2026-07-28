from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(32), unique=True , nullable=False)
    password = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    address = db.Column(db.String(64), nullable=False)
    pincode = db.Column(db.Integer , nullable=False)
    role = db.Column(db.Boolean, nullable=False, default=1)
    history = db.relationship("ReserveParkingSpot", backref="user", cascade = "all,delete",lazy = True)

class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(32), unique=True , nullable=False)
    price = db.Column(db.Integer, nullable=False)
    pin_code = db.Column(db.Integer, nullable=False)
    available_spots = db.Column(db.Integer, nullable=False)
    spot = db.relationship("ParkingSpot", backref="lot", cascade = "all,delete",lazy = True)

class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lot.id"), nullable=False)
    status = db.Column(db.String(64), nullable=False)  # O- Occupied, A- Available
    history = db.relationship("ReserveParkingSpot", backref="spot", cascade = "all,delete",lazy = True)

class ReserveParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey("parking_spot.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    vehicle_number = db.Column(db.String(20), nullable=False)
    parking_timestamp = db.Column(db.DateTime, nullable=False)
    leaving_timestamp = db.Column(db.DateTime, nullable=True)
    parking_cost = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(64), nullable=False)  # O- Occupied, A- Available