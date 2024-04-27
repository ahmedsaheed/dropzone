import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore

firebase_request_adapter = requests.Request()
firestore_db = firestore.Client()

# would be used for sharing files amongst users
def get_all_users():
    users = firestore_db.collection('users').stream()
    # convert the users to a list
    users_list = []
    for user in users:
        users_list.append(user.to_dict())
    return users_list



def get_user(user_token):
    user = firestore_db.collection('users').document(user_token['user_id'])

    print(user_token['email'], user_token['user_id'])

    if not user.get().exists:
        user_data = {
            'email': user_token['email'],
            'id': user_token['user_id'],
        }
        firestore_db.collection('users').document(user_token['user_id']).set(user_data)

    # can we print all the users here?
    print(get_all_users())
    users = firestore_db.collection('users').stream()

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
