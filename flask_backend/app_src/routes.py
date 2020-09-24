from datetime import datetime, timedelta
from flask import render_template, request, redirect, flash, url_for
from flask_login import login_user, current_user, login_required, logout_user
from sqlalchemy import desc
#from sqlalchemy.orm import sessionmaker


from app_src import app, db, bcrypt
from app_src.models import User, Gym, Activity, ActivityTimeSlot, Reservation


@app.route('/')
def home():
    # if current_user.is_authenticated and not current_user.is_admin:
    if current_user.is_authenticated :
    #if current_user.email == 's@g.com':
        return redirect(url_for('index'))
    else:
        next_page = request.args.get('next')
        return render_template('login.html', next_page=next_page)


@app.route('/logging_in', methods=["POST", 'GET'])
def logging_in():

    email = request.form["email"]
    pwd = request.form["password"]

    usr = User.query.filter_by(email=email).first()
    if usr:
        pw_hash = bcrypt.generate_password_hash(usr.password)

    if usr is None:
        flash('Invalid Login')
        return redirect(url_for('home'))
    elif bcrypt.check_password_hash(pw_hash, pwd):
        login_user(user=usr, remember=True)
        next_page = request.form.get('next')

        if next_page:
            return redirect(next_page)
        else:
            if current_user.is_admin:
                return redirect(url_for('ad_index'))
            else:
                return redirect(url_for('index'))
    else:
        flash('Incorrect Login Credentials')
        return redirect(url_for('home'))


@app.route('/index')
@login_required
def index():
    # return render_template('index.html', current_user=current_user)
    return app.send_static_file('index.html')
    

'''
# this is not in current version
@app.route('/ad_index')
@login_required
def ad_index():
    if current_user.is_admin:
        return render_template('ad_index.html', current_user=current_user)
    else:
        return redirect(url_for('index'))
'''


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/update_user', methods=["POST", 'GET'])
@login_required
def update_user():
    
    if request.method == 'POST':
        user_name = request.form["user_name"]
        first_name = request.form["first_name"]
        sur_name = request.form["sur_name"]
        dob = request.form["dob"]
        phone_number_1 = request.form["phone1"]
        phone_number_2 = request.form["phone2"]
        profile_picture_file_path = request.form["profile_pic"]
        medic_certificate_file_path = request.form["medic_certificate"]
        email = request.form["email"]
    else:
        return render_template('updateUser.html')    


    # profile and medic store on certain location and save that path with filename on db
    #dob = datetime.strptime(dob, '%Y-%m-%d')

    exist = User.query.filter_by(email=email).first()
    if exist:
        flash('Email already Taken')
        return redirect(url_for('home'))
        # return redirect(url_for('update_user_html'))
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

        flash('User Details updated successfully')
        return redirect(url_for('update_user'))


@app.route('/add_gym', methods=["POST", 'GET'])
@login_required
def add_gym():

    if request.method == 'POST':
        name = request.form["name"]
        description = request.form["description"]
        picture_1_file_path = request.form.get("picture_1_file_path",False)
        picture_2_file_path = request.form.get("picture_2_file_path",False)
        picture_3_file_path = request.form.get("picture_3_file_path",False)
        location = request.form["location"]
        email = request.form.get("email",False)
        phone_number = request.form.get("phone_number",False)
        
    else:
        return render_template('createGym.html')
        
    gym = Gym(name=name,
              owner = current_user,
              description=description,
              picture_1_file_path=picture_1_file_path,
              picture_2_file_path=picture_2_file_path,
              picture_3_file_path=picture_3_file_path,
              location=location,
              email=email,
              phone_number=phone_number)
    
    
    db.session.add(gym)
    db.session.commit()
    flash('Gym Added successfully')
    return redirect(url_for('add_gym'))


@app.route('/update_gym/<int:id>', methods=["POST", 'GET'])
@login_required
def update_gym(id):

    if request.method == 'POST':
        name = request.form.get("name",False)
        description = request.form.get("description",False)
        location = request.form.get("location",False)
        email = request.form.get("email",False)
        phone_number = request.form.get("phone_number",False)
    else:
        return render_template('updateGym.html')

    gym = Gym.query.filter_by(id=id).first()

    gym.name=name   
    gym.description=description
    gym.location=location
    gym.email=email
    gym.phone_number=phone_number

    db.session.commit()
    flash('Gym Details Updated successfully')
    return redirect(url_for('add_gym'))


@app.route('/add_activity/<int:id>', methods=["POST", 'GET'])
@login_required
def add_activity(id):

    if request.method == 'POST':
        name = request.form["name"]
        description = request.form["description"]
        picture_1_file_path = request.form.get("picture_1_file_path",False)
        picture_2_file_path = request.form.get("picture_2_file_path",False)
    else:
        return render_template('addActivity.html')

    # currently we have only one gym so we can directly query from gym table based on user id
    # while update to multi gym under one user we need to ask from user this is for which gym 
    gym = Gym.query.filter_by(owner_id=current_user.id, id=id).first()


    activity = Activity(gymowner = gym,
                        name=name,
                        description=description)
    
    db.session.add(activity)
    db.session.commit()
    flash('Activity Added successfully')
    return redirect(url_for('add_gym'))


# update activity 
# this is not in current version
@app.route('/update_activity/<int:gym_id>/<int:id>', methods=["POST", 'GET'])
@login_required
def update_activity(gym_id,id):
     
    #usergym = Gym.query.filter_by(owner_id=current_user.id).first()
    #gymactivity = Activity.query.filter_by(id=id , gym_id=usergym.id).first()

    # this is need to send in hidden in form of previous page ie. update_activty_html
    if request.method == 'POST':
        name = request.form["name"]
        description = request.form["description"]
        picture_1_file_path = request.form.get("picture_1_file_path", False)
        picture_2_file_path = request.form.get("picture_2_file_path", False)
    else:
        return render_template('updateActivity.html')

    # currently we have only one gym so we dont want to update
    # while update to multi gym under one user we need to ask from user this is for which gym  

    activity = Activity.query.filter_by(gym_id=gym_id,id=id).first()
 
    activity.name=name
    activity.description=description
   
    db.session.commit()
    flash('Activity Details Updated successfully')
    return redirect(url_for('add_gym'))


# delete activity
# this is not in current version
@app.route('/delete_activity/<int:gym_id>/<int:id>', methods=["POST", 'GET'])
@login_required
def delete_activity(gym_id,id):

    # this is need to send in hidden in form of previous page ie. delete_activty_html
    activity = Activity.query.filter_by(id=id, gym_id=gym_id).first()

    try:
        db.session.delete(activity)
        db.session.commit()
        flash('Activity Deleted successfully')
        return redirect(url_for('add_gym'))
    except:
        flash('Activity Deleted failed')
        return redirect(url_for('add_gym'))
        


@app.route('/add_activity_timeslot/<int:gym_id>/<int:act_id>', methods=["POST", 'GET'])
@login_required
def add_activity_timeslot(gym_id,act_id):

    #userGym = Gym.query.filter_by(owner_id=current_user.id).first()
    activity = Activity.query.filter_by(gym_id=gym_id, id=act_id).first()

    #gymowner = userGym


    # this is need to send in hidden in form of previous page ie. add_activity_timeslot_html
    if request.method == 'POST':
        date = request.form["date"]
        time = request.form["time"]
    else:
        return render_template('addActTS.html')
    
    date = datetime.strptime(date, '%Y-%m-%d')
    time = datetime.strptime(time, '%H:%M')
    
    activity_timeslot = ActivityTimeSlot(act=activity,
                                         date=date,
                                         time=time)
    
    db.session.add(activity_timeslot)
    db.session.commit()
    flash('Activity TimeSlot Added successfully')
    return redirect(url_for('add_gym'))


@app.route('/update_activity_timeslot/<int:act_id>/<int:act_ts_id>', methods=["POST", 'GET'])
@login_required
def update_activity_timeslot(act_id,act_ts_id):

    
    # this is need to send in hidden in form of previous page ie. update_activity_timeslot_html 
    # or we can take that from quering activitytimeslot table by using id 
    if request.method == 'POST':
        #activity_id = timeslot.activity.id
        date = request.form["date"]
        time = request.form["time"]
        #room_count = request.form["room_count"]
    else:
        return render_template('updateTS.html')

    date = datetime.strptime(date, '%Y-%m-%d')
    time = datetime.strptime(time, '%H:%M')   
    

    activity_timeslot = ActivityTimeSlot.query.filter_by(id=act_ts_id, activity_id=act_id).first()
    
    activity_timeslot.date = date
    activity_timeslot.time = time
    #activity_timeslot.room_count = room_count

    db.session.commit()
    flash('Activity TimeSlot Updated successfully')
    return redirect(url_for('add_gym'))


@app.route('/delete_activity_timeslot/<int:act_id>/<int:act_ts_id>', methods=["POST", 'GET'])
@login_required
def delete_activity_timeslot(act_id, act_ts_id):

    #userGym = Gym.query.filter_by(owner_id=current_user.id).first()
    #gymactivity = Activity.query.filter_by(gym_id=userGym.id).first() 
    #timeOfGa = ActivityTimeSlot.query.filter_by(activity_id=gymactivity.id).first()
    # this is need to send in hidden in form of previous page ie. delete_activity_timeslot_html
    #id = timeOfGa.id 

    activity_timeslot = ActivityTimeSlot.query.filter_by(id=act_ts_id, activity_id=act_id).first()
    
    db.session.delete(activity_timeslot)
    db.session.commit()
    flash('Activity TimeSlot Deleted successfully')
    return redirect(url_for('add_gym'))


# add reservation
@app.route('/add_reservation/<int:gym_id>/<int:act_id>/<int:act_ts_id>', methods=['GET'])
@login_required
def add_reservation(gym_id, act_id, act_ts_id):


    userGym = Gym.query.filter_by(id=gym_id).first()
    gymActivity = Activity.query.filter_by(gym_id=userGym.id, id=act_id).first()
    actTimeSlot = ActivityTimeSlot.query.filter_by(activity_id=gymActivity.id, id=act_ts_id).first()
    

    #timeOfGa = ActivityTimeSlot.query.filter_by(id=timeslot.id and activity_id=activites.id and gyms.owner_id=current_user.id).first()
    # this is need to send in hidden in form of previous page ie. add_reservation_html

    reservation = Reservation(reserve_user=current_user,
                              reserve_activity=gymActivity,
                              reserve_time_slot=actTimeSlot)
    
    db.session.add(reservation)
    db.session.commit()
    flash('Reservation Added successfully')
    return redirect(url_for('add_gym'))


# delete reservation (Deadline : before 3hrs)
@app.route('/delete_reservation', methods=["POST", 'GET'])
@login_required
def delete_reservation():

    userGym = Gym.query.filter_by(owner_id=current_user.id).first()
    gymactivity = Activity.query.filter_by(gym_id=userGym.id).first() 
    timeOfGa = ActivityTimeSlot.query.filter_by(activity_id=gymactivity.id).first()
    # this is need to send in hidden in form of previous page ie. delete_reservation_html
    id = timeOfGa.id 

    reservation = Reservation.query.filter_by(id=id).first()
    
    activity_timeslot = ActivityTimeSlot.query.filter_by(id=reservation.activity_timeslot_id).first()
    
    time = activity_timeslot.time
    #time_ = activity_timeslot.time
    #datetime_ = date_ + ' ' + time_
    time = datetime.strptime(time, '%H:%M')

    now = datetime.now()
    modify_now = now + timedelta(minutes = 180)
    modify_now = modify_now.strftime('%H:%M')
    modify_now = datetime.strptime(modify_now, '%H:%M')

    if modify_now <= time:
        db.session.delete(reservation)
        db.session.commit()
        flash('Reservation Deleted successfully')
        return redirect(url_for('add_activity'))
    
    time = activity_timeslot.time
    if time:
        db.session.delete(reservation)
        db.session.commit()
        flash('Reservation Deleted successfully')
        return redirect(url_for('add_activity'))
    else:
        flash('Reservation Cancelation is only allowed for 3hours before the event')
        return redirect(url_for('add_activity'))


# show activites
@app.route('/list_activities/', methods=["POST",'GET'])
@login_required
def list_activities():
    
    # this can also done by more accurate recent update first by take activytimeslot from desc 
    # and use activityid from that and query or join with it
    #activities = Activity.query.paginate()
    #act_timeslots = ActivityTimeSlot.query.order_by(ActivityTimeSlot.date).paginate()
    #return render_template('listActs.html', activities=activities)

    #Session = sessionmaker(bind = engine)
    #session = Session()

    #activities = session.query(Activity, ActivityTimeSlot).filter(Activity.id == ActivityTimeSlot.activity_id).paginate()
    #activities = select * from activity left join activity_time_slot on activity.id == activity_time_slot.activity_id

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

    '''
    for act in activities:
        time = str(act.ActivityTimeSlot.time)
        #time = datetime.strptime(time, '%H:%M:%SEC')
        #date = datetime.strptime(str(act.ActivityTimeSlot.date), '%Y-%m-%d')
        date = str(act.ActivityTimeSlot.date)
        val = [act.Activity.name, time, date]
        if val not in acts.values():
            acts[val.] = val
            i += 1
    return acts
    '''
    #return render_template('listActs.html', activities=activities)

# show my reservations
@app.route('/my_reservations', methods=["POST", 'GET'])
@login_required
def my_reservations():

    '''
    #not needed
    activities = Activity.query.paginate()
    activity_timeslot = ActivityTimeSlot.query.order_by(ActivityTimeSlot.date).paginate()
    reservations = Reservation.query.filter_by(user_id=current_user.id).paginate()
    return render_template('myReserves.html', reservations=reservations, activities=activities, activity_timeslot=activity_timeslot)
    '''

    user = User.query.filter_by(id = current_user.id).first()
    reserved_activites_details = {}
    reservations = user.reser_user
    '''
    for i in range(len(reservations)):
        val = ActivityTimeSlot.query.filter_by(id=reservations[i].id).first()
        act = Activity.query.filter_by(id=val.activity_id).first()
        d[x] = str(val.id) +'   '+ str(val.date) +'     '+ str(val.time) + '    '+str(act.name)
        x += 1
    return d

    '''
    for reservation in reservations:
        activity_timeslot = ActivityTimeSlot.query.filter_by(id=reservation.activity_timeslot_id).first()
        activity = Activity.query.filter_by(id=activity_timeslot.activity_id).first()

        reserved_activity = {
            'Name': activity.name,
            'Description': activity.description,
            'Date': activity_timeslot.date,
            'Time': activity_timeslot.time
        }
        reserved_activites_details[activity_timeslot.id] = reserved_activity

    # reserved_activites_details[0]['activity'].name
    # reserved_activites_details[0]['activity'].description
    # reserved_activites_details[0]['activity'].gym_id # .pic1 # .pic2
    # reserved_activites_details[0]['activity_timeslot'].date
    # reserved_activites_details[0]['activity_timeslot'].time
    return reserved_activites_details
    

# show my activity time slots
# this is only for one activty in current version
'''
@app.route('/my_activity_timeslots', methods=["POST", 'GET'])
@login_required
def my_activity_timeslots():

    # this activity id is need to send in hidden in form of previous page ie. html page    
    activity_id = request.form['activity_id']
    activity_timeslots = ActivityTimeSlot.query.filter_by(activity_id=activity_id).order_by(ActivityTimeSlot.date).order_by(ActivityTimeSlot.time).all()
    return activity_timeslots
'''


# show my activities
# show reservation for my activity
# this is not in current version

@app.route('/show_my_activities',methods=['POST','GET'])
@login_required
def show_my_activities():
    
    '''
    gyms = Gym.query.filter_by(owner_id=current_user.id).paginate()
    activities = Activity.query.paginate()
    activity_timeslot = ActivityTimeSlot.query.order_by(ActivityTimeSlot.date).paginate()
    return render_template('showMyActivities.html', gyms=gyms, activities=activities, activity_timeslot=activity_timeslot )
    '''
    my_activities = {}

    #for gym in gyms:
    activities = db.session.query(User, Gym, Activity, ActivityTimeSlot).select_from(ActivityTimeSlot).join(Activity , Activity.id == ActivityTimeSlot.activity_id).join(Gym, Activity.gym_id == Gym.id).join(User, Gym.owner_id == current_user.id).all()
    #activities = Activity.query.filter_by(gym_id=gym.id).all()

    for activity in activities:
        my_activity = {
            'Name': activity.Activity.name,
            'Description': activity.Activity.description,
            'Date': activity.ActivityTimeSlot.date,
            'Time': activity.ActivityTimeSlot.time
        }
        my_activities[activity.ActivityTimeSlot.id] = my_activity
    return my_activities
