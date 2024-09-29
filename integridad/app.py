import os
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from sqlalchemy import MetaData
from hashlib import md5

# Access the value of an environment variable
mail_username = os.environ.get('MAIL_USERNAME')
mail_password = os.environ.get('MAIL_PASSWORD')

# HASH key for integrity check
HASH_SECRET_KEY = os.getenv("HASH_SECRET_KEY")

app = Flask(__name__)

#PostgreSQL configuration
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{os.getenv('POSTGRES_USER', 'postgres')}:"
    f"{os.getenv('POSTGRES_PASSWORD', 'postgres')}@postgres_db:5432/{os.getenv('POSTGRES_DB', 'my_db')}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = mail_username
app.config['MAIL_PASSWORD'] = mail_password
db = SQLAlchemy(app)

EMAILS = [mail_username]

def generate_hash(table, obj):
    # Get the model's columns (excluding the 'hash' column)
    columns = [column.name for column in table.columns]
    values = []

    for column in columns:
        if column != 'hash':  # Exclude the 'hash' column
            value = getattr(obj, column, None)
            values.append(str(value) if value is not None else '')

    # Join the values and append the secret key
    data_string = ''.join(values) + HASH_SECRET_KEY

    # Generate and return the MD5 hash
    return md5(data_string.encode()).hexdigest()

def send_alert(table_name, row_id):
    # Send alert
    with app.app_context():
        mail = Mail(app)
        msg = Message('Integrity Alert', sender=mail_username, recipients=EMAILS)
        msg.body = "There is an integrity issue in the database. \n\t"
        msg.body += f"Table: {table_name}, Row ID: {row_id}"
        mail.send(msg)
    print("Alert sent for table: ", table_name, " row_id: ", row_id, flush=True)

def check_row_integrity(table, row):
    # Check integrity of row
    with app.app_context():
        row_data = db.session.query(table).filter_by(id=row).first()
        # Calculate hash of row without the hash field
        db_hash = row_data.hash
        row_hash = generate_hash(table, row_data)
        
        print("Row ID:", row, "Row Hash: ", row_hash, " DB Hash: ", db_hash, flush=True)
        
        if row_hash != row_data.hash:
            print("Integrity issue in table: ", table.name, " row_id: ", row, flush=True)
            send_alert(table.name, row)

def check_table(table):
    # Check integrity of table
    with app.app_context():
        print("Checking table: ", table.name, flush=True)
        # print("DB Metadata: ", dir(table), flush=True)
        rows = db.session.query(table.c.id).all()
        for row in rows:
            check_row_integrity(table, row.id)

def scan_integrity():
    # Check all tables
    with app.app_context():
        metadata = MetaData()
        metadata.reflect(db.engine)
        tables = metadata.tables.values()
        for table in tables:
            check_table(table)

sched = BackgroundScheduler(daemon=True)
sched.add_job(scan_integrity, 'interval', seconds=60)
sched.start()

@app.route('/')
def index():
    return "Integrity Endpoint..."

@app.route('/check-integrity')
def check_integrity():
    print("Checking integrity...", flush=True)
    scan_integrity()
    return "Integrity check done..."

if __name__ == "__main__":
    # Test the alert
    app.run(debug=False, host="0.0.0.0")
