from flask import Flask,redirect
from flask import render_template, request
from flask import request
from flask import session
import database as db
import authentication
import logging
from pymongo import MongoClient
from database import update_appointment
from flask import jsonify
from database import appointments_coll, customers_coll, get_user_appointments, update_appointment, cancel_appointment


app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["dental_office"]
appointments_coll = db["appointments"]
doctors_coll = db['doctors']

database = client['appt_management']
customers_coll = db['customers']

# Set the secret key to some random bytes.
# Keep this really secret!
app.secret_key = b's@g@d@c0ff33!'

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)

@app.route('/')
def index():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["services"] 
    services_coll = db["services"]
    services = list(services_coll.find())

    return render_template('index.html', page="Index", services=services)

@app.route('/appointments')
def appointments():
    appointments_coll = db["appointments"]
    appointments = list(appointments_coll.find())
    return render_template('appointments.html', appointments=appointments)

@app.route('/reserve', methods=['POST'])
def reserve():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        day = request.form['day']
        time = request.form['time']
        room = request.form['room']
        dentist = request.form['dentist']
        
        user = session['user']
        patient = f"{user['username']}"
        
        update_appointment(day, time, room, dentist, patient)
        
        return redirect('/appointments')
    else:
        return 'Method not allowed'

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")

@app.route('/dentist_sched')
def dentist_sched():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["dental_office"]
    appointments_coll = db["appointments"]

    unique_dentists = appointments_coll.distinct("dentist")

    selected_dentist = request.args.get('dentist')

    if selected_dentist:
        appointments = list(appointments_coll.find({"dentist": selected_dentist, "reserved": True}))
    else:
        appointments = list(appointments_coll.find({"reserved": True}))

    return render_template('dentist_sched.html', page="Dentist Schedules", appointments=appointments, dentists=unique_dentists, selected_dentist=selected_dentist)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            error = "Incomplete login data. Please enter both username and password."
        else:
            is_successful, user = authentication.login(username, password)
            if is_successful:
                session["user"] = user
                return redirect('/')
            else:
                error = "Invalid username or password. Please try again."

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect('/')

@app.route('/my_appointments')
def my_appointments():
    if 'user' not in session:
        return redirect('/login')

    username = session['user']['username']
    appointments = db.get_user_appointments(username)

    return render_template('my_appointments.html', appointments=appointments)

@app.route('/our_doctors')
def our_doctors():
    doctors = list(doctors_coll.find())
    return render_template('doctors.html', doctors=doctors)

@app.route('/cancel_reservation', methods=['POST'])
def cancel_reservation():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
        
        cancel_appointment(appointment_id)
        
        return redirect('/appointments')
    else:
        return 'Method not allowed'
    
