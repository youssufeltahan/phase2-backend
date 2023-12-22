from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from .utils import sign_up
import uuid
from pymongo import MongoClient
from datetime import datetime, timedelta
import jwt
from django.conf import settings
from django.contrib.auth.models import User
from dotenv import load_dotenv
import os
load_dotenv()  # This line brings all environment variables from .env into os.environ
#print(os.environ['port'])

def generate_jwt_token(user):
    payload = {
        'user_id': user,
        'exp': datetime.utcnow() + timedelta(days=7),
    }

    token = jwt.encode(payload, '7amotaelota', algorithm='HS256')
    return token


def decode_jwt_token(token):
    try:
        payload = jwt.decode(token, '7amotaelota', algorithms=['HS256'])
        user_id = payload['user_id']
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_from_request(request):
    authorization_header = request.headers.get('Authorization')
    if authorization_header and authorization_header.startswith('Bearer '):
        # Extract the token after 'Bearer '
        token = authorization_header.split(' ')[1]
        return token
    return None

def get_user(request):
    token = get_token_from_request(request)
    
    id_user = decode_jwt_token(token)
    
    return id_user

#local URI = mongodb://localhost:27017/
#mongodb+srv://7amota04:eMfNLR02bJyUr9bc@cluster0.bgxx4tr.mongodb.net/
url='mongodb+srv://AmrMahmoud:amr.mahmoud@cluster0.exwcjr4.mongodb.net/?retryWrites=true&w=majority'
#url = os.environ.get('db_port')

client = MongoClient(url)
db = client['clinic']

print("bolbol")
print(os.environ.get('db_port'))

@api_view(['POST'])
def signUp(request):
    if request.method == 'POST':
        

        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        isDoctor = request.data.get('isDoctor')

        result = sign_up(username, email, password, isDoctor)

        if result['success']:
            return Response({'message': result['message']}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': result['message']}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def sign_in(request):
    if request.method == 'POST':
    
        # Get user credentials from the request
        username = request.data.get('username')
        password = request.data.get('password')

        # Check if the user exists in the database
        patient_data = db.patients.find_one({'username': username, 'password': password})
        doctor_data = db.doctors.find_one({'username': username, 'password': password})

        # User found, you may want to return additional user information
        if patient_data:
            token = generate_jwt_token(username)
            return JsonResponse({'token': token})
        
        elif doctor_data:
            if doctor_data:
                # Store the doctor's ID in the variable
                doctor_id = doctor_data.get('id')
                token = generate_jwt_token(username)
                return JsonResponse({'token': token , 'isDoctor' : doctor_data.get('isDoctor')})
            else:
                return Response({'message': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)
        
        else:
            return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def addSlot(request):
    
    username = get_user(request)
    user = db.doctors.find_one({"username": username})
    doctor_id = user.get('id')
    if user:
        
        slot_id = uuid.uuid4()
        # Extract date, start_time, end_time from request.data
        date = request.data.get('date')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        isBooked = request.data.get('isBooked')

        # Insert slot into MongoDB
        slot_data = {
            'slot_id' : str(slot_id),
            'doctor_id': doctor_id,
            'date': date,
            'start_time': start_time,
            'end_time': end_time,
            "isBooked" : isBooked,
            'patient_name' : None
        }

        result = db.doctor_schedule.insert_one(slot_data)

        if result.inserted_id:
            return Response({'message': 'Slot inserted successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'message': 'Failed to insert slot'}, status=status.HTTP_400_BAD_REQUEST)
        
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['GET'])
def getDoctorName(request):
    
    collection = db['doctors']
    result = collection.find({}, {'_id': 0, 'username': 1})
    names = [doc.get('username') for doc in result]

    return Response({'usernames': names}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_available_slots(request, docslots):
    #doctor_id = request.data.get('doctor_id')

    username = get_user(request)
    user = db.doctors.find_one({"username": docslots})
    doctor_id = user.get('id')
    if user:
        #available_slots = list(db.doctor_schedule.find( {'doctor_id': doctor_id}))
        slots_cursor = db.doctor_schedule.find({'doctor_id': doctor_id, 'isBooked' : False})
        available_slots = [
            {
                'slot_id': slot['slot_id'],
                'date': slot['date'],
                'start_time': slot['start_time'],
                'end_time': slot['end_time'],
                'isBooked': slot['isBooked'],
            }
            for slot in slots_cursor
        ]

        available_slot = [
            {'date': slot['date'], 'start_time': slot['start_time'], 'end_time': slot['end_time']}
            for slot in slots_cursor
        ]

        if not available_slots:
            return Response({'Doctor schedule is busy'}, status=status.HTTP_200_OK)    
        

        return Response({'slots': available_slots}, status=status.HTTP_200_OK)
    
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['POST'])
def choose_slot(request):
    #patient_username = request.data.get('patient_username')
    username = get_user(request)
    patient_username = db.patients.find_one({"username": username})
    
    if patient_username:
        doctor_id = request.data.get('doctor_id')
        chosen_slot_id = request.data.get('slot_id')
        print(doctor_id)
        print(chosen_slot_id)  
        patient_data = patient_username
        # Check if the slot is available
        if patient_data:
            slot = db.doctor_schedule.find_one({'slot_id': chosen_slot_id, 'isBooked': False})

            if slot:
                # Update the slot to mark it as booked
                result = db.doctor_schedule.update_one(
                    {'slot_id': chosen_slot_id},
                    {'$set': {'isBooked': True, 'patient_name': patient_data.get('username')}}
                )

                # patient_id = patient_data['id']
                db.patient_schedule.insert_one(db.doctor_schedule.find_one({'slot_id': chosen_slot_id}))
                if result.modified_count > 0:
                    return Response({'message': 'Slot chosen successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'message': 'Failed to choose slot'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'message': 'Slot is not available or does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'patient does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_403_FORBIDDEN)


@api_view(['PUT'])
def update_appointment(request):
    username = get_user(request)
    patient_username = db.patients.find_one({"username": username})
    
    if patient_username:
        new_doctor_name = request.data.get('newDoctorName')
        new_slot_id = request.data.get('newSlotId')
        old_slot_id = request.data.get('oldSlotId')
        print("oldid")
        print(old_slot_id)
        
        # Check if the patient exists
        patient_data = patient_username
        if not patient_data:
            return Response({'message': 'Patient does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        print(new_doctor_name)
        print(new_slot_id)
        # Check if the new doctor exists
        new_doctor = db.doctors.find_one({'username': new_doctor_name})
        doctor_id = new_doctor.get('id')
        if not new_doctor:
            return Response({'message': 'New doctor does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the new slot is available
        new_slot = db.doctor_schedule.find_one({'slot_id': new_slot_id, 'doctor_id': doctor_id, 'isBooked': False})
        if not new_slot:
            return Response({'message': 'New slot is not available or does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        name = patient_data.get('username')
        # Get the current appointment for the patient
        current_appointment = db.doctor_schedule.find_one({'slot_id': old_slot_id, 'isBooked': True})
        
        if current_appointment:
            db.patient_schedule.delete_one(db.doctor_schedule.find_one({'slot_id': old_slot_id}))
            # Update the current appointment to mark it as available
            db.doctor_schedule.update_one(
                {'slot_id': old_slot_id},
                {'$set': {'isBooked': False, 'patient_name': None}}
            )

            # Update the patient's appointment to the new doctor and slot
            db.doctor_schedule.update_one(
                {'slot_id': new_slot_id},
                {'$set': {'isBooked': True, 'patient_name': patient_data.get('username')}}
            )
            db.patient_schedule.insert_one(db.doctor_schedule.find_one({'slot_id': new_slot_id}))

            return Response({'message': 'Appointment updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Patient does not have an existing appointment'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['DELETE'])
def cancel_appointment(request):
    username = get_user(request)
    patient_username = db.patients.find_one({"username": username})
    cancelSlot = request.query_params.get('cancelSlot')
    
    if patient_username:
        patient_data = patient_username
        if not patient_data:
            return Response({'message': 'Patient does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # Get the current appointment for the patient
        current_appointment = db.doctor_schedule.find_one({'patient_name': patient_data.get('username'), 'isBooked': True})
        db.patient_schedule.delete_one(db.doctor_schedule.find_one({'slot_id': cancelSlot}))
        if current_appointment:
            # Update the current appointment to mark it as available
            result = db.doctor_schedule.update_one(
                {'slot_id': cancelSlot},
                {'$set': {'isBooked': False, 'patient_name': None}}
            )

            db.patient_schedule.delete_one({'patient_username' : patient_data.get('username')})

            if result.modified_count > 0:
                return Response({'message': 'Appointment canceled successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Failed to cancel appointment'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Patient does not have an existing appointment'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
def get_patient_slots(request):
    username = get_user(request)
    patient_username = db.patients.find_one({"username": username})
    
    if patient_username:

        # Assuming you have a collection named 'doctor_schedule'
        #available_slots = list(db.doctor_schedule.find( {'doctor_id': doctor_id}))
        print(patient_username.get('username'))
        slots_cursor = db.patient_schedule.find({'patient_name': patient_username.get('username')})
        available_slots = [
            {'slot_id': slot['slot_id'],'date': slot['date'], 'start_time': slot['start_time'], 'end_time': slot['end_time']}
            for slot in slots_cursor
        ]

        return Response({'slots': available_slots, 'patient_name ': patient_username.get('username')},
                         status=status.HTTP_200_OK)
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=status.HTTP_403_FORBIDDEN)
    
