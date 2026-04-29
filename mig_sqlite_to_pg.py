import os
from app import db
from models import Helper, Attendance, Payment

from flask import Flask
from models import db, Helper, Attendance, Payment

# SQLite app
sqlite_app = Flask(__name__)
sqlite_app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:/Users/tanma/Documents/Projects/Househelp/instance/househelp.db"
sqlite_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(sqlite_app)

# ---- Step 1: Read from SQLite ----
with sqlite_app.app_context():
    print("Reading from SQLite...")

    helpers = Helper.query.all()
    attendances = Attendance.query.all()
    payments = Payment.query.all()

    print("Helpers:", len(helpers))
    print(f"Attendances: {len(attendances)}")
    print(f"Payments: {len(payments)}")

# ---- Step 2: Switch to Postgres ----
postgres_app = Flask(__name__)

POSTGRES_URL = "postgresql://housemanager_user:2mhKcw6wz9MuYmLWKq1CyEMVfZbc22Mp@dpg-d7ot1e5ckfvc73fsjmog-a/housemanager"

if POSTGRES_URL.startswith("postgres://"):
    POSTGRES_URL = POSTGRES_URL.replace("postgres://", "postgresql://", 1)

postgres_app.config['SQLALCHEMY_DATABASE_URI'] = POSTGRES_URL
postgres_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(postgres_app)

with postgres_app.app_context():
    db.create_all()

    helper_map = {}

    for h in helpers:
        new_h = Helper(name=h.name, type=h.type, default_qty=h.default_qty)
        db.session.add(new_h)
        db.session.flush()
        helper_map[h.id] = new_h.id

    db.session.commit()

    for a in attendances:
        new_a = Attendance(
            helper_id=helper_map.get(a.helper_id),
            date=a.date,
            present=a.present,
            shift=a.shift,
            qty=a.qty
        )
        db.session.add(new_a)

    db.session.commit()

    for p in payments:
        new_p = Payment(
            helper_id=helper_map.get(p.helper_id),
            date=p.date,
            amount=p.amount
        )
        db.session.add(new_p)

    db.session.commit()

    print("✅ Migration done!")