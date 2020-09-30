from datetime import datetime, timedelta
from flask import render_template, request, redirect, flash, url_for, jsonify
from flask_login import login_user, current_user, login_required, logout_user
from sqlalchemy import desc

from app_src import app, db, bcrypt
from app_src.models import User, Gym, Activity, ActivityTimeslot, Reservation


@app.errorhandler(404)
def not_found(e):
    return redirect(url_for('home'))


@app.route('/index')
@app.route('/')
def home():
    try:

        # if current_user.is_authenticated and not current_user.is_admin:
        if current_user.is_authenticated :
            return render_template('index.html')
        else:
            next_page = request.args.get('next')
            return render_template('login.html', next_page=next_page)

    except Exception as msg:
        flash(msg)
        return render_template('login.html')


@app.route('/logging_in', methods=["POST"])
def logging_in():
    try:

        email = request.form.get("email")
        pwd = request.form.get("password")
        usr = User.query.filter_by(email=email).first()
        if usr is None:
            flash('Invalid Login')
            return redirect(url_for('home'))
        elif bcrypt.check_password_hash(usr.password, pwd):
            login_user(user=usr, remember=True)
            next_page = request.form.get('next')
            if next_page:
                return redirect(next_page)
            else:
            return redirect(url_for('home'))
        else:
            flash('Incorrect Login Credentials')
            return redirect(url_for('home'))

    except Exception as msg:
        flash(msg)
        return redirect(url_for('home'))
    

@app.route('/logout')
@login_required
def logout():
    try:

        logout_user()
        return redirect(url_for('home'))

    except Exception as msg:
        flash(msg)
        return redirect(url_for('home'))








@app.route('/api/get_current_user')
def get_currenr_user():
    try:

        return_data = {
            'success': True,
            'message': '',
            'data' = {
                'user_id': current_user.id, 
                'user_name': current_user.user_name,
                'first_name': current_user.first_name,
                'sur_name': current_user.sur_name,
                'email': current_user.email,
                'dob': current_user.dob.strftime('%Y-%m-%d'),
                'phone_number_1': current_user.phone_number_1,
                'phone_number_2': current_user.phone_number_2,
                'is_verified ': current_user.is_verified,
            }    
        }
        return jsonify(return_data), 200

    except Exception as msg:
        return_data = {'success': False, 'message': msg, 'data' = {} }
        return jsonify(return_data), 500
        

@app.route('/api/get_gym_details')
def get_gym_details():
    try:

        gym = GYM.query.filter_by(owner_id=current_user.id).first()
        if gym:
            return_data = {
                'success': True, 
                'message': '',
                'data': {
                    'gym_id': gym.id,
                    'name': gym.name,
                    'description': gym.description,
                    'picture_1_file_path': gym.picture_1_file_path,
                    'picture_2_file_path': gym.picture_2_file_path,
                    'picture_3_file_path': gym.picture_3_file_path,
                    'location ': gym.location,
                    'email': gym.email,
                    'phone_number': gym.phone_number,
                }
            }
        else:
            return_data = { 'success': True, 'message': 'No Gym for Current User', 'data' = {} }
        
        return jsonify(return_data), 200

    except Exception as msg:
        return_data = { 'success': False, 'message': msg, 'data' = {} }
        return jsonify(return_data), 500


@app.route('/api/update_user', methods=["POST"])
@login_required
def update_user():
    try:

        user_name = request.form.get("user_name", current_user.user_name)
        first_name = request.form.get("first_name", current_user.first_name)
        sur_name = request.form.get("sur_name", current_user.sur_name)
        dob = request.form.get("dob", current_user.dob)
        phone_number_1 = request.form.get("phone1", current_user.phone_number_1)
        phone_number_2 = request.form.get("phone2", current_user.phone_number_2)
        profile_picture_file_path = request.form.get("profile_pic", current_user.profile_picture_file_path)
        medic_certificate_file_path = request.form.get("medic_certificate", current_user.medic_certificate_file_path)
        email = request.form.get("email", current_user.email)

        # profile and medic store on certain location and save that path with filename on db
        dob = datetime.strptime(dob, '%Y-%m-%d')

        exist = User.query.filter_by(email=email).first()
        if exist:
            msg = 'Email already Taken'
        else:
            current_user.user_name = user_name
            current_user.first_name = first_name
            current_user.sur_name = sur_name
            current_user.dob = dob
            current_user.phone_number_1 = phone_number_1
            current_user.phone_number_2 = phone_number_2
            current_user.profile_picture_file_path = profile_picture_file_path
            current_user.medic_certificate_file_path = medic_certificate_file_path
            current_user.email = email

            db.session.commit()

            msg = 'User Details updated successfully'

        return_data = { 'success': True, 'message': msg, 'data' = {} }
        return jsonify(return_data), 200

    except Exception as msg:
        return_data = { 'success': False, 'message': msg, 'data' = {} }
        return jsonify(return_data), 500


@app.route('/add_gym', methods=["POST"])
@login_required
def add_gym():
    try:

        name = request.form.get("name", '')
        description = request.form.get("description", '')
        picture_1_file_path = request.form.get("picture_1_file_path", '')
        picture_2_file_path = request.form.get("picture_2_file_path", '')
        picture_3_file_path = request.form.get("picture_3_file_path", '')
        location = request.form.get("location", '')
        email = request.form.get("email", '')
        phone_number = request.form.get("phone_number", '')
        
        gym = Gym(owner_ref = current_user,
                name=name,
                description=description,
                picture_1_file_path=picture_1_file_path,
                picture_2_file_path=picture_2_file_path,
                picture_3_file_path=picture_3_file_path,
                location=location,
                email=email,
                phone_number=phone_number)
        
        db.session.add(gym)
        db.session.commit()

        msg = 'Gym Added successfully'
        
        return_data = { 'success': True, 'message': msg, 'data' = {} }
        return jsonify(return_data), 200

    except Exception as msg:
        return_data = { 'success': False, 'message': msg, 'data' = {} }
        return jsonify(return_data), 500


@app.route('/update_gym', methods=["POST"])
@login_required
def update_gym():
    try:

        gym = GYM.query.filter_by(owner_id=current_user.id).first()
        if gym:
            name = request.form.get("name", gym.name)
            description = request.form.get("description", gym.description)
            picture_1_file_path = request.form.get("picture_1_file_path", gym.picture_1_file_path)
            picture_2_file_path = request.form.get("picture_2_file_path", gym.picture_2_file_path)
            picture_3_file_path = request.form.get("picture_3_file_path", gym.picture_3_file_path)
            location = request.form.get("location", gym.location)
            email = request.form.get("email", gym.email)
            phone_number = request.form.get("phone_number", gym.phone_number)

            gym.name = name
            gym.description = description
            gym.picture_1_file_path = picture_1_file_path
            gym.picture_2_file_path = picture_2_file_path
            gym.picture_3_file_path = picture_3_file_path
            gym.location = location
            gym.email = email
            gym.phone_number = phone_number

            db.session.commit()
            msg = 'Gym Details Updated successfully'
        
        return_data = { 'success': True, 'message': msg, 'data' = {} }
        return jsonify(return_data), 200

    except Exception as msg:
        return_data = { 'success': False, 'message': msg, 'data' = {} }
        return jsonify(return_data), 500


@app.route('/add_activity', methods=["POST"])
@login_required
def add_activity():
    try:

        name = request.form.get("name", '')
        description = request.form.get("description", '')
        picture_1_file_path = request.form.get("picture_1_file_path", '')
        picture_2_file_path = request.form.get("picture_2_file_path", '')
            
        # currently we have only one gym so we can directly query from gym table based on user id
        # while update to multi gym under one user we need to ask from user this is for which gym ie. 
        # gym = GYM.query.filter_by(id=gym_id).first()   
        gym = GYM.query.filter_by(owner_id=current_user.id).first()

        activity = Activity(gym_ref=gym,
                            name=name,
                            description=description,
                            picture_1_file_path=picture_1_file_path,
                            picture_2_file_path=picture_2_file_path)
        
        db.session.add(activity)
        db.session.commit()
        msg = 'Activity Added successfully'
        
        return_data = { 'success': True, 'message': msg, 'data' = {} }
        return jsonify(return_data), 200

    except Exception as msg:
        return_data = { 'success': False, 'message': msg, 'data' = {} }
        return jsonify(return_data), 500



# update activity 
# this is not in current version
@app.route('/update_activity', methods=["POST"])
@login_required
def update_activity():
    try:

        # this is need to send in form of previous page 
        activity_id = request.form.get('activity_id', False)
        if activity_id:
            activity = Activity.query.filter_by(id=activity_id).first()
            if activity:
                name = request.form.get("name", activity.name)
                description = request.form.get("description", activity.description)
                picture_1_file_path = request.form.get("picture_1_file_path", activity.picture_1_file_path)
                picture_2_file_path = request.form.get("picture_2_file_path", activity.picture_2_file_path)

                activity.name = name
                activity.description = description
                activity.picture_1_file_path = picture_1_file_path
                activity.picture_2_file_path = picture_2_file_path
            
                db.session.commit()
                msg = 'Activity Details Updated successfully'
            else:
                msg = 'No such Activity'
        else:
            msg = 'activity_id not found in request data'

        return_data = { 'success': True, 'message': msg, 'data' = {} }
        return jsonify(return_data), 200

    except Exception as msg:
        return_data = { 'success': False, 'message': msg, 'data' = {} }
        return jsonify(return_data), 500
        

# delete activity
# this is not in current version
# need to delete its corresponding timeslots too
@app.route('/delete_activity', methods=["POST"])
@login_required
def delete_activity():
    try:

        # this is need to send in form of previous page 
        activity_id = request.form.get('activity_id', False)
        if activity_id:
            activity = Activity.query.filter_by(id=activity_id).first()
            if activity:
                db.session.delete(activity)
                db.session.commit()
                msg = 'Activity Deleted successfully'
            else:
                msg = 'No such Activity'
        else:
            msg = 'activity_id not found in request data'

        return_data = { 'success': True, 'message': msg, 'data' = {} }
        return jsonify(return_data), 200

    except Exception as msg:
        return_data = { 'success': False, 'message': msg, 'data' = {} }
        return jsonify(return_data), 500


@app.route('/add_activity_timeslot', methods=["POST"])
@login_required
def add_activity_timeslot():
    try:

        # this is need to send in form of previous page 
        activity_id = request.form.get('activity_id', False)
        if activity_id:
            activity = Activity.query.filter_by(id=activity_id).first()
            if activity:
                date = request.form.get("date", '')
                time = request.form.get("time", '')
                room_count = request.form.get("room_count", '')
                fee = request.form.get("fee", '')
                
                date = datetime.strptime(date, '%Y-%m-%d')
                time = datetime.strptime(time, '%H:%M')
                
                activity_timeslot = ActivityTimeslot(activity_ref=activity,
                                                    date=date,
                                                    time=time,
                                                    room_count=room_count,
                                                    fee=fee)
                
                db.session.add(activity_timeslot)
                db.session.commit()
                msg = 'Activity TimeSlot Added successfully'
            else:
                msg = 'No such Activity'
        else:
            msg = 'activity_id not found in request data'

        return_data = { 'success': True, 'message': msg, 'data' = {} }
        return jsonify(return_data), 200

    except Exception as msg:
        return_data = { 'success': False, 'message': msg, 'data' = {} }
        return jsonify(return_data), 500
        

@app.route('/update_activity_timeslot', methods=["POST"])
@login_required
def update_activity_timeslot():
    try:

        # this is need to send in form of previous page 
        activity_timeslot_id = request.form.get('activity_timeslot_id', False)
        if activity_timeslot_id:
            activity_timeslot = ActivityTimeslot.query.filter_by(id=activity_timeslot_id).first()
            if activity_timeslot:
                date = request.form.get("date", activity_timeslot.date)
                time = request.form.get("time", activity_timeslot.time)
                room_count = request.form.get("room_count", activity_timeslot.room_count)
                fee = request.form.get("fee", activity_timeslot.fee)

                date = datetime.strptime(date, '%Y-%m-%d')
                time = datetime.strptime(time, '%H:%M')   
                
                activity_timeslot.date = date
                activity_timeslot.time = time
                activity_timeslot.room_count = room_count
                activity_timeslot.fee = fee

                db.session.commit()
                msg = 'Activity TimeSlot Updated successfully'
            else:
                msg = 'No such Activity Timeslot'
        else:
            msg = 'activity_timeslot_id not found in request data'

        return_data = { 'success': True, 'message': msg, 'data' = {} }
        return jsonify(return_data), 200

    except Exception as msg:
        return_data = { 'success': False, 'message': msg, 'data' = {} }
        return jsonify(return_data), 500


@app.route('/delete_activity_timeslot', methods=["POST"])
@login_required
def delete_activity_timeslot():
    try:

        # this is need to send in form of previous page 
        activity_timeslot_id = request.form.get('activity_timeslot_id', False)
        if activity_timeslot_id:
            activity_timeslot = ActivityTimeslot.query.filter_by(id=activity_timeslot_id).first()
            if activity_timeslot:
                db.session.delete(activity_timeslot)
                db.session.commit()
                msg = 'Activity TimeSlot Deleted successfully'
            else:
                msg = 'No such Activity Timeslot'
        else:
            msg = 'activity_timeslot_id not found in request data'

        return_data = { 'success': True, 'message': msg, 'data' = {} }
        return jsonify(return_data), 200

    except Exception as msg:
        return_data = { 'success': False, 'message': msg, 'data' = {} }
        return jsonify(return_data), 500


# add reservation
@app.route('/add_reservation', methods=["POST"])
@login_required
def add_reservation():
    try:

        # this is need to send in form of previous page 
        activity_timeslot_id = request.form.get('activity_timeslot_id', False)
        if activity_timeslot_id:
            activity_timeslot = ActivityTimeslot.query.filter_by(id=activity_timeslot_id).first()
            if activity_timeslot:
                reservation = Reservation(user_ref=current_user,
                                        activity_timeslot_ref=activity_timeslot)
                if reservation:                   
                    db.session.add(reservation)
                    db.session.commit()
                    msg = 'Reservation Added successfully'
                else:
                    msg = 'No such Reservation'
            else:
                msg = 'No such Activity Timeslot'
        else:
            msg = 'activity_timeslot_id not found in request data'

        return_data = { 'success': True, 'message': msg, 'data' = {} }
        return jsonify(return_data), 200

    except Exception as msg:
        return_data = { 'success': False, 'message': msg, 'data' = {} }
        return jsonify(return_data), 500


# delete reservation (Deadline : before 3hrs)
@app.route('/delete_reservation', methods=["POST"])
@login_required
def delete_reservation():
    try:

        # this is need to send in form of previous page 
        reservation_id = request.form.get('reservation_id', False)
        if reservation_id:
            reservation = Reservation.query.filter_by(id=reservation_id).first()
            if reservation:
                date_ = reservation.activity_timeslot_ref.date
                time_ = reservation.activity_timeslot_ref.time
                datetime_ = date_ + ' ' + time_
                datetime_ = datetime.strptime(datetime_, '%Y-%m-%d %H:%M')

                now = datetime.now()
                modify_now = now + timedelta(minutes = 180)
                modify_now = modify_now.strftime('%Y-%m-%d %H:%M')
                modify_now = datetime.strptime(modify_now, '%Y-%m-%d %H:%M')

                if modify_now <= datetime_:
                    db.session.delete(reservation)
                    db.session.commit()
                    msg = 'Reservation Deleted successfully'
                else:
                    msg = 'Reservation Cancelation is only allowed for 3hours before the event'
            else:
                msg = 'No such Reservation'
        else:
            msg = 'reservation_id not found in request data'

        return_data = { 'success': True, 'message': msg, 'data' = {} }
        return jsonify(return_data), 200

    except Exception as msg:
        return_data = { 'success': False, 'message': msg, 'data' = {} }
        return jsonify(return_data), 500

        











# show activites
@app.route('/list_activities', methods=["POST"])
@login_required
def list_activities():
    
    activities = db.session.query(Activity, ActivityTimeSlot).outerjoin(ActivityTimeSlot, Activity.id == ActivityTimeSlot.activity_id).order_by(desc(ActivityTimeSlot.id)).all()
    all_current_activites = {}

    for val in activities:
        activity = {
            'Name' : val.Activity.name,
            'Description' : val.Activity.description,
            'Date' : val.ActivityTimeSlot.date,
            'Time' : val.ActivityTimeSlot.time
        }
        all_current_activites[val.ActivityTimeSlot.id] = activity 

    return all_current_activites


# show my reservations
@app.route('/my_reservations', methods=["POST"])
@login_required
def my_reservations():

    reserved_activites_details = {}
    reservations = current_user.reservations
   
    for reservation in reservations:
        activity_timeslot = ActivityTimeSlot.query.filter_by(id=reservation.activity_timeslot_id).first()
        activity = Activity.query.filter_by(id=activity_timeslot.activity_id).first()
        # join

        reserved_activity = {
            'Name': activity.name,
            'Description': activity.description,
            'Date': activity_timeslot.date,
            'Time': activity_timeslot.time
        }
        reserved_activites_details[activity_timeslot.id] = reserved_activity

    return reserved_activites_details
    

# show my activity time slots
# this is only for one activty in current version
'''
@app.route('/my_activity_timeslots', methods=["POST"])
@login_required
def my_activity_timeslots():

    # this activity id is need to send in hidden in form of previous page ie. html page    
    activity_id = request.form['activity_id']
    activity_timeslots = ActivityTimeSlot.query.filter_by(activity_id=activity_id).order_by(ActivityTimeSlot.date).order_by(ActivityTimeSlot.time).all()
    return activity_timeslots
'''


# show my activities
@app.route('/show_my_activities',methods=['POST'])
@login_required
def show_my_activities():
    
    my_activities = {}

    activities = db.session.query(Gym, Activity, ActivityTimeSlot).select_from(ActivityTimeSlot).join(Activity , Activity.id == ActivityTimeSlot.activity_id).join(Gym, Activity.gym_id == Gym.id).all()
    
    for activity in activities:
        if activity.Gym.owner_id == current_user.id:
            my_activity = {
                'Name': activity.Activity.name,
                'Description': activity.Activity.description,
                'Date': activity.ActivityTimeSlot.date,
                'Time': activity.ActivityTimeSlot.time
            }
            my_activities[activity.ActivityTimeSlot.id] = my_activity

    return my_activities


# show reservation for my activity
# this is not in current version
