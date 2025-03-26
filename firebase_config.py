import firebase_admin
from firebase_admin import credentials, firestore

# Load Firebase credentials
cred = credentials.Certificate("ai-disaster-mangement-firebase-adminsdk-fbsvc-c639f7ca48.json")  
firebase_admin.initialize_app(cred)

# Initialize Firestore database
db = firestore.client()
