from datetime import datetime

from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(80))
    patients = db.relationship('PatientData', backref='user', lazy=True)

class DepresionScore(db.Model):
    __tablename__ = 'depression_scores'
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    date = db.Column(db.DateTime, default=datetime.utcnow())
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))

class TwitterUser(db.Model):
    __tablename__ = 'twitter_users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    screen_name = db.Column(db.String(150))
    profile_image_url_https = db.Column(db.String(250))
    tweets = db.relationship('Tweet', backref='twitter_user', lazy=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))

class Tweet(db.Model):
    __tablename__ = 'tweets'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(280))
    created_at = db.Column(db.DateTime)
    twitter_user_id = db.Column(db.Integer, db.ForeignKey('twitter_users.id'))

class PatientData(db.Model):
    __tablename__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(150))
    birthday_date = db.Column(db.DateTime)
    gender = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    depression_scores = db.relationship('DepresionScore', backref='patient', lazy=True)
    twitter_users = db.relationship('TwitterUser', backref='patient', lazy=True)