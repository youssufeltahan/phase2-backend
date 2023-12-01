from pymongo import MongoClient
import uuid

def sign_up(username, email, password, isDoctor):
        client = MongoClient('mongodb+srv://7amota04:eMfNLR02bJyUr9bc@cluster0.bgxx4tr.mongodb.net/')
        db = client['clinic']
        new_id = uuid.uuid4()
        
        if db.patients.find_one({'$or': [{'username': username}, {'email': email}]}):
            return {'success': False, 'message': 'Username or email already exists'}
        
        if db.doctors.find_one({'$or': [{'username': username}, {'email': email}]}):
            return {'success': False, 'message': 'Username or email already exists'}
        
        user_data = {
            'id' : str(new_id),
            'username': username,
            'email': email,
            'password': password,
            'isDoctor' : isDoctor
        }

        if isDoctor:
             result = db.doctors.insert_one(user_data)
        else:
             result = db.patients.insert_one(user_data)
        if result.inserted_id:
            return {'success': True, 'message': 'User created successfully'}
        else:
            return {'success': False, 'message': 'Failed to create user'}
        
# def sign_in(username, password):
#      client = MongoClient('mongodb://localhost:27017/')
#      db = client['clinic']

#      # Get user credentials from the request
#      if db.patients.find_one({'$or': [{'username': username}, {'password': password}]}):
#         return db.patients.find_one({'username': username, 'password': password})    
        
#      if db.doctors.find_one({'$or': [{'username': username}, {'password': password}]}):
#         return db.doctors.find_one({'username': username, 'password': password})    
