from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Helper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., cook, domestic helper, milk vendor
    default_qty = db.Column(db.Float, default=1.0)  # default litres for milk vendors

    attendances = db.relationship('Attendance', backref='helper', lazy=True)
    payments = db.relationship('Payment', backref='helper', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    helper_id = db.Column(db.Integer, db.ForeignKey('helper.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    present = db.Column(db.Boolean, default=False)
    shift = db.Column(db.String(50), nullable=True)
    qty = db.Column(db.Float, nullable=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    helper_id = db.Column(db.Integer, db.ForeignKey('helper.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float, nullable=False)