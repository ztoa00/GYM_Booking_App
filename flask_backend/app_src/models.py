from flask_login import UserMixin
from app_src import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    sur_name = db.Column(db.String(50))
    dob = db.Column(db.DateTime)
    phone_number_1 = db.Column(db.String(20))
    phone_number_2 = db.Column(db.String(20))
    profile_picture_file_path = db.Column(db.String(200))
    medic_certificate_file_path = db.Column(db.String(200))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    gyms = db.relationship('Gym', backref='owner',lazy=True)
    reser_user = db.relationship('Reservation', backref='reserve_user', lazy=True)


# foreign key to user table
class Gym(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500))
    picture_1_file_path = db.Column(db.String(200))
    picture_2_file_path = db.Column(db.String(200))
    picture_3_file_path = db.Column(db.String(200))
    location = db.Column(db.String(500))
    email = db.Column(db.String(100),nullable=False)
    phone_number = db.Column(db.String(20))
    activities = db.relationship('Activity', backref='gymowner', lazy=True)


# foreign key to user table
# if cost of activity fixed mean add it here
class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gym.id'),nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500))
    picture_1_file_path = db.Column(db.String(200))
    picture_2_file_path = db.Column(db.String(200))
    time_slot = db.relationship('ActivityTimeSlot', backref='act', lazy=True)
    reser_activity = db.relationship('Reservation',backref='reserve_activity', lazy=True)    


# foreign key to activity table
# if cost of activity not fixed and ot vary based on time mean add it here
class ActivityTimeSlot(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    room_count = db.Column(db.Integer)
    reser_timeslot = db.relationship('Reservation', backref='reserve_time_slot',lazy=True)


# foreign key to user table
# foreign key to activity table
# foreign key to activity time solt table
class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    activity_id = db.Column(db.Integer,db.ForeignKey('activity.id'))
    activity_timeslot_id = db.Column(db.Integer,db.ForeignKey('activity_time_slot.id'))

db.create_all()
db.session.commit()
