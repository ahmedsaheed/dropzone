import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore 

firebase_request_adapter = requests.Request()
firestore_db = firestore.Client()

def get_user(user_token):
    user = firestore_db.collection('users').document(user_token['user_id'])
    if not user.get().exists:
        user_data = {
            'name': "John Doe"
        }
        firestore_db.collection('users').document(user_token['user_id']).set(user_data)
    return user

def validate_firebase_token(id_token):
    if not id_token:
        return None

    user_token = None
    try:
        user_token = google.oauth2.id_token.verify_firebase_token(
            id_token, firebase_request_adapter
        )
    except ValueError as err:
        print(str(err))

    return user_token


