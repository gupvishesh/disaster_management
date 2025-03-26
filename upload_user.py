import json
from firebase_config import db

# Load JSON user data
with open("userdata.json", "r") as file:
    users = json.load(file)

# Upload data to Firestore
for user in users:
    db.collection("users").add(user)

print("✅ User data uploaded successfully!")
