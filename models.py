from datetime import datetime
from flask_sqlalchemy import SQLAlchemy #sqlAlchemy database layer, Lets Flask communicate easily with the database SQLite

#Create the database object-Creates a connection between your Flask app and the SQLite database
db = SQLAlchemy()

#User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    fullname = db.Column(db.String(100), unique=False, nullable=False)
    password = db.Column(db.String(100), nullable=False)

#Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='To Do')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    estimate_start = db.Column(db.Date, nullable=True)
    estimate_end = db.Column(db.Date, nullable=True)
    # Relationship to access user info
    user = db.relationship('User', backref=db.backref('tasks', lazy=True))