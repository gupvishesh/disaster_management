from flask import Flask, request,jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from geopy.distance import geodesic
import requests
from firebase_config import db
# import firebase_admin
# from firebase_admin import firestore, credentials

app = Flask(__name__)


def get_phone_numbers():
    phone_numbers = []
    users_ref = db.collection("users").stream()  # Fetch all users
    for user in users_ref:
        phone_numbers.append(user.to_dict().get("phone"))
    return phone_numbers


# Twilio Credentials
account_sid = "ACda1d8de2bd8b45e5b33b83fdb7633170"
auth_token = "f6d04843c23d9ef905f09a482d055b23"
twilio_client = Client(account_sid, auth_token)

TWILIO_NUMBER = "+18648033507"

# Handle Incoming WhatsApp & SMS Messages
@app.route("/webhook/whatsapp", methods=["POST"])
@app.route("/webhook/sms", methods=["POST"])
def bot_reply():
    incoming_msg = request.values.get("Body", "").lower()
    sender = request.values.get("From", "")

    response = MessagingResponse()
    msg = response.message()

    # Simple Response Logic
    if "help" in incoming_msg:
        msg.body("⚠️ Disaster Alert Bot: You can receive real-time alerts and emergency contacts here. Reply with 'status' to check current warnings.")
    elif "status" in incoming_msg:
        msg.body("🌪 No current disasters in your area. Stay safe!")
    else:
        msg.body("I didn’t understand. Reply 'help' for options.")

    return str(response)

# EXOTEL_SID = "jagruthai2"
# EXOTEL_API_KEY = "04db4e6538ae72c2452474dd994068f1beb3afa6a64a44b8"
# EXOTEL_API_TOKEN = "517337efeb9110a6e45232bfa4373511c1ed4eaab555b520"
# EXOPHONE = "+9104041892775"  # Your Exotel virtual number

# def make_call(to_number, alert_message):
#     url = f"https://{EXOTEL_API_KEY}:{EXOTEL_API_TOKEN}@api.exotel.com/v1/Accounts/{EXOTEL_SID}/Calls/connect"
    
#     data = {
#         "From": EXOPHONE,  # Your Exotel virtual number
#         "To": to_number,   # User’s phone number
#         "CallerId": EXOPHONE,
#         "Url": "http://your-server.com/ivr.xml",  # IVR flow XML (We’ll set this up next)
#         "Priority": "Normal",
#     }
    
#     response = requests.post(url, data=data)
#     return response.json()

ZEGOCLOUD_APP_ID = "1129540149"
ZEGOCLOUD_KEY= "04AAAAAGfk9fMADC4A/3kYvvMCGb5T5gCzxxghKj+2pBjDRoWOf0In+bbl/HSw5mTHsaoSt+BYt9mY/jfDjz7GbasTmwoxa0x7+HnxvsE/N6rZgAIdnlGGZ2M3mGD6txNVKsIQHMKOD3EVHrUOQL3y1ULxMfxexcuGgvXBtYsy1Kl40PKRSyqf3QpK5c6jqSOEIDJL3WArnJNKQc4IAHL9tIp6XiXscaL4DZarWfXvm73pD76e5ehqTMTE1S59TKBHSsiIgB6Vy3rwKPgB"
ZEGOCLOUD_API_URL = "wss://webliveroom1129540149-api.coolzcloud.com/ws"

def make_call():
    """Initiates a voice call using ZEGOCLOUD API."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ZEGOCLOUD_KEY}"  # Use the generated token
    }

    data = {
        "app_id": ZEGOCLOUD_APP_ID,
        "caller_id": CALLER_ID,
        "callee_id": CALLEE_ID,
        "call_type": "voice",  # Use "video" for video calls
        "push_message": {
            "title": "Incoming Call",
            "body": "You have a voice call"
        }
    }

    # Send the request
    response = requests.post(ZEGOCLOUD_API_URL, headers=headers, json=data)

    # Print response
    if response.status_code == 200:
        print("✅ Call initiated successfully:", response.json())
    else:
        print("❌ Failed to make call:", response.status_code, response.json())

# make_call("+919346293133")

# @app.route("/call", methods=["POST"])
# def send_disaster_alert():o
#     data = request.json
#     phone_number = data.get("phone")
#     alert_message = data.get("message")

#     if not phone_number or not alert_message:
#         return {"error": "Phone and message required"}, 400

#     response = make_call(phone_number)
#     return response

@app.route("/ivr", methods=["GET", "POST"])
def ivr():

    disaster_message = "Warning! A severe disaster is expected in your area. Please evacuate immediately."

    exotel_response = '''<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say voice="female">Warning! A severe disaster is expected in your area. Please take immediate precautions and evacuate if necessary.</Say>
        <Pause length="2"/>
        <Say voice="female">Stay safe and follow official guidelines. Press 1 for assistance.</Say>
    </Response>'''
    
    return Response(exotel_response, mimetype="text/xml")

# def send_alerts(phone_numbers, message):
@app.route("/send-alert", methods=["POST"])
def send_disaster_alert():
    data = request.json
    message = data.get("message")
    disaster_lat = data.get("lat")  
    disaster_lon = data.get("lon")  
    radius_km = data.get("radius", 10) 

    if not all([message, disaster_lat, disaster_lon]):
        return jsonify({"error": "Message, lat, and lon are required"}), 400
    
    # phone_numbers = get_affected_users(disaster_lat, disaster_lon, radius_km)
    phone_numbers=["+917997997101"]

    if not phone_numbers:
        return jsonify({"message": "✅ No users in affected area"}), 200
    

    for phone in phone_numbers:
        # Send SMS
        twilio_client.messages.create(
            body=message,
            from_=TWILIO_NUMBER,
            to=phone
        )

        #send whatsapp alert
        message = twilio_client.messages.create(
        from_='whatsapp:+14155238886',
        # content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
        # content_variables='{ "1": "Disaster Warning!", "2": "Stay indoors and follow official instructions." }',
        to=f'whatsapp:{phone}',
        body="🚨 Disaster Alert! Please stay safe and follow evacuation instructions."
        )

        make_call(phone)
        print(message.sid)
    return jsonify({"message": "✅ Alerts sent successfully!"}), 200

# Example Usage
phone_numbers = ["+917997997101"]
# send_disaster_alert()
message = "⚠️ Urgent: Flood warning in your area. Seek shelter immediately!"
# send_alerts(phone_numbers, message)

# to add user data after signup,delete account and get users list ig it will be done by dashboard 
# if code needed check chatgpt,this code will call the below function

def add_user(name, phone, location, lat, lon):
    user_data = {
        "name": name,
        "phone": phone,
        "location": location,
        "lat": lat,
        "lon": lon
    }
    db.collection("users").add(user_data)  
    print(f"✅ User {name} added successfully!")

# add_user("Palak", "+916305364663", "Cherrapunji", 25.1702, 91.4316)

def get_affected_users(disaster_lat, disaster_lon, radius_km):
    """Fetches users within the disaster-affected radius."""
    affected_users = []
    users_ref = db.collection("users").stream()  # Get all users

    for user in users_ref:
        user_data = user.to_dict()
        user_lat, user_lon = user_data.get("lat"), user_data.get("lon")
        user_phone = user_data.get("phone")

        if user_lat and user_lon and user_phone:
            user_location = (user_lat, user_lon)
            disaster_location = (disaster_lat, disaster_lon)

            # Calculate distance (in km)
            distance = geodesic(user_location, disaster_location).km

            if distance <= radius_km:  # Only add users within the radius
                affected_users.append(user_phone)

    return affected_users


# Run the Flask app
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)


