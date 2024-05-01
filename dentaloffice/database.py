import pymongo
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient("mongodb://localhost:27017/")

dental_office_db = client['dental_office']
appointments_coll = dental_office_db["appointments"]
doctors_coll = dental_office_db['doctors']

appt_management_db = client['appt_management']
customers_coll = appt_management_db['customers']

def get_user(username):
    user = customers_coll.find_one({"username": username})
    if user:
        user['_id'] = str(user['_id'])
    return user


def update_appointment(day, time, room, dentist, patient):
    try:
        appointments_coll.update_one(
            {"day": day, "time": time, "room": room, "dentist": dentist},
            {"$set": {"patient": patient, "reserved": True}}
        )
    except Exception as e:
        logging.error(f"Error updating appointment: {e}")

def cancel_appointment(appointment_id):
    try:
        appointments_coll.update_one(
            {"_id": ObjectId(appointment_id)},
            {"$unset": {"patient": "", "reserved": False}}
        )
    except Exception as e:
        logging.error(f"Error canceling appointment: {e}")

def get_appointments():
    try:
        appointments = list(appointments_coll.find())
        for appointment in appointments:
            appointment['_id'] = str(appointment['_id'])
        return appointments
    except Exception as e:
        logging.error(f"Error fetching appointments: {e}")
        return []

def get_user_appointments(username):
    appointments = list(appointments_coll.find({"patient": username}))
    for appointment in appointments:
        appointment['_id'] = str(appointment['_id'])
    return appointments
