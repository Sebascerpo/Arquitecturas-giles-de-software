from flask import Flask, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, DateTime, Text
from datetime import datetime
import requests
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class MonitorLogs(db.Model):
    id = Column(Integer, primary_key=True)
    url = Column(Text)
    status = Column(Integer, nullable=True)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


@app.before_request
def create_tables():
    db.create_all()


def store_log(url, status, response):
    with app.app_context():

        log_entry = MonitorLogs(url=url, status=status, response=response)
        db.session.add(log_entry)
        db.session.commit()


def monitor_endpoint():
    with app.app_context():
        try:

            # trymonitor_endpoint:
            print("Running monitoring function...")

            url = "http://ip.jsontest.com"
            # url = "http://127.0.0.1:5002/health"
            response = requests.get(url)
            data = response.json()
            status = response.status_code

            if status == 200:
                store_log(url, status, str(data))

            else:
                print("Alert! Unhealthy status detected.")
                store_log(url, status, str(data))  # Store error logs

        except Exception as e:
            print(f"Error occurred: {e}")

            store_log(url, 404, str(e))  # Log errors


# sched = BackgroundScheduler(daemon=True)
# sched.add_job(monitor_endpoint, 'interval', seconds=60)
# sched.start()

# Routes


@app.route('/')
def index():
    return "Monitoring Endpoint..."


@app.route('/logs', methods=['GET'])
def get_logs():
    logs = MonitorLogs.query.order_by(MonitorLogs.timestamp.desc()).all()
    log_list = [
        {
            "id": log.id,
            "status": log.status,
            "response": log.response,
            "timestamp": log.timestamp
        }
        for log in logs
    ]
    return jsonify(log_list)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
