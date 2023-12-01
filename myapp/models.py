import pymongo
from djongo import models
#connect_string = 'mongodb+srv://<username>:<password>@<atlas cluster>/<myFirstDatabase>?retryWrites=true&w=majority' 

from django.conf import settings

my_client = pymongo.MongoClient("mongodb://localhost:27017/")

dbname = my_client['clinic']

collection_name = dbname["patients"]

# medicine_1 = {
#     "medicine_id": "RR000123456",
#     "common_name" : "Paracetamol",
#     "scientific_name" : "",
#     "available" : "Y",
#     "category": "fever"
# }
# medicine_2 = {
#     "medicine_id": "RR000342522",
#     "common_name" : "Metformin",
#     "scientific_name" : "",
#     "available" : "Y",
#     "category" : "type 2 diabetes"
# }

# # Insert the documents
# collection_name.insert_many([medicine_1,medicine_2])
# # Check the count
# # count = collection_name.count()
# # print(count)

# # Read the documents
# med_details = collection_name.find({})
# # Print on the terminal
# for r in med_details:
#     print(r["common_name"])
# # Update one document
# update_data = collection_name.update_one({'medicine_id':'RR000123456'}, {'$set':{'common_name':'Paracetamol 500'}})

# # Delete one document
# delete_data = collection_name.delete_one({'medicine_id':'RR000123456'})
# users/models.py
from djongo import models

# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    # Add custom fields here, if needed

    def __str__(self):
        return self.username
