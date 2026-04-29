from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import text
from models import db, Helper, Attendance, Payment
from datetime import datetime, date
import calendar
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# ✅ FIX: Proper SQLite path for Render
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'househelp.db')

db.init_app(app)

ATTENDANCE_CUTOFF_DATE = date(2026, 4, 27)


def is_shift_helper(helper_type):
    return helper_type and helper_type.strip().lower() in ['cook', 'domestic helper']


def is_milk_vendor(helper_type):
    return helper_type and helper_type.strip().lower() == 'milk vendor'


def ensure_database_schema():
    with db.engine.connect() as conn:
        if conn.dialect.name == 'sqlite':
            def has_column(table_name, column_name):
                result = conn.execute(text(f"PRAGMA table_info({table_name})")).fetchall()
                return any(row[1] == column_name for row in result)

            try:
                if not has_column('helper', 'default_qty'):
                    conn.execute(text('ALTER TABLE helper ADD COLUMN default_qty FLOAT DEFAULT 1.0'))
                if not has_column('attendance', 'shift'):
                    conn.execute(text('ALTER TABLE attendance ADD COLUMN shift VARCHAR(50)'))
                if not has_column('attendance', 'qty'):
                    conn.execute(text('ALTER TABLE attendance ADD COLUMN qty FLOAT'))
            except Exception:
                pass  # safe fallback


# ✅ FIX: Ensure DB is created ONCE in production
_db_initialized = False

@app.before_request
def setup():
    global _db_initialized
    if not _db_initialized:
        db.create_all()
        ensure_database_schema()
        _db_initialized = True


@app.route('/')
def index():
    helpers = Helper.query.all()
    return render_template('index.html', helpers=helpers)


@app.route('/add_helper', methods=['GET', 'POST'])
def add_helper():
    if request.method == 'POST':
        name = request.form['name']
        type_ = request.form['type']

        if type_ == 'other':
            type_ = request.form.get('customType', 'Other').strip() or 'Other'

        default_qty = 1.0 if is_milk_vendor(type_) else None

        helper = Helper(name=name, type=type_, default_qty=default_qty)
        db.session.add(helper)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_helper.html')


@app.route('/edit_helper/<int:id>', methods=['GET', 'POST'])
def edit_helper(id):
    helper = Helper.query.get_or_404(id)

    if request.method == 'POST':
        helper.name = request.form['name']
        type_ = request.form['type']

        if type_ == 'other':
            type_ = request.form.get('customType', 'Other').strip() or 'Other'

        helper.type = type_

        if is_milk_vendor(type_):
            try:
                helper.default_qty = float(request.form.get('default_qty', 1.0))
            except ValueError:
                helper.default_qty = 1.0
        else:
            helper.default_qty = None

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_helper.html', helper=helper)


@app.route('/helper/<int:id>')
def helper_detail(id):
    helper = Helper.query.get_or_404(id)
    recent_attendances = Attendance.query.filter_by(helper_id=id).order_by(Attendance.date.desc()).limit(10).all()
    recent_payments = Payment.query.filter_by(helper_id=id).order_by(Payment.date.desc()).limit(10).all()
    return render_template('helper_detail.html', helper=helper, recent_attendances=recent_attendances, recent_payments=recent_payments)


@app.route('/attendance/<int:year>/<int:month>')
def attendance(year, month):
    helpers = Helper.query.all()
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]

    # ✅ Handle empty DB safely
    if not helpers:
        return render_template(
            'attendance.html',
            year=year,
            month=month,
            cal=cal,
            helpers=[],
            attendances={},
            month_name=month_name,
            cutoff_year=ATTENDANCE_CUTOFF_DATE.year,
            cutoff_month=ATTENDANCE_CUTOFF_DATE.month,
            cutoff_day=ATTENDANCE_CUTOFF_DATE.day,
        )

    attendances = {}
    for helper in helpers:
        attendances[helper.id] = {}
        for att in helper.attendances:
            if att.date.year == year and att.date.month == month:
                key = f"{att.date.year}-{att.date.month:02d}-{att.date.day:02d}"
                attendances[helper.id][key] = {
                    'present': att.present,
                    'shift': att.shift,
                    'qty': att.qty,
                }

    return render_template('attendance.html',
                           year=year,
                           month=month,
                           cal=cal,
                           helpers=helpers,
                           attendances=attendances,
                           month_name=calendar.month_name[month])


@app.route('/mark_attendance/<int:year>/<int:month>/<int:day>/<int:helper_id>', methods=['POST'])
def mark_attendance(year, month, day, helper_id):
    date_obj = date(year, month, day)

    if date_obj < ATTENDANCE_CUTOFF_DATE:
        return redirect(url_for('attendance', year=year, month=month))

    helper = Helper.query.get_or_404(helper_id)
    attendance = Attendance.query.filter_by(helper_id=helper_id, date=date_obj).first()

    if not attendance:
        attendance = Attendance(helper_id=helper_id, date=date_obj)
        db.session.add(attendance)

    present = request.form.get('present', '0') == '1'
    shift = request.form.get('shift') if is_shift_helper(helper.type) else None
    qty = None

    if is_milk_vendor(helper.type):
        try:
            qty = float(request.form.get('qty', ''))
            present = qty > 0
        except:
            qty = None

    attendance.present = present
    attendance.shift = shift
    attendance.qty = qty

    db.session.commit()
    return redirect(url_for('attendance', year=year, month=month))


@app.route('/payments/<int:year>/<int:month>')
def payments(year, month):
    helpers = Helper.query.all()
    cal = calendar.monthcalendar(year, month)

    payments_dict = {}
    for helper in helpers:
        payments_dict[helper.id] = {
            f"{pay.date.year}-{pay.date.month:02d}-{pay.date.day:02d}": pay.amount
            for pay in helper.payments
            if pay.date.year == year and pay.date.month == month
        }

    return render_template('payments.html',
                           year=year,
                           month=month,
                           cal=cal,
                           helpers=helpers,
                           payments=payments_dict,
                           month_name=calendar.month_name[month])


@app.route('/add_payment/<int:year>/<int:month>/<int:day>/<int:helper_id>', methods=['GET', 'POST'])
def add_payment(year, month, day, helper_id):
    date_obj = date(year, month, day)

    if request.method == 'POST':
        amount = float(request.form['amount'])
        payment = Payment(helper_id=helper_id, date=date_obj, amount=amount)
        db.session.add(payment)
        db.session.commit()
        return redirect(url_for('payments', year=year, month=month))

    helper = Helper.query.get(helper_id)
    return render_template('add_payment.html', year=year, month=month, day=day, helper=helper)


# Local run only
if __name__ == '__main__':
    app.run(debug=True)