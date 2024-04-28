from typing_extensions import Any
from google.auth.jwt import Mapping
import google.oauth2.id_token
from google.auth.transport import requests
from google.cloud import firestore

firebase_request_adapter = requests.Request()
firestore_db = firestore.Client()

# Returns the current user's data from the firestore database
def get_user(user_token):
    user = firestore_db.collection('users').document(user_token['user_id'])
    print(user_token['email'], user_token['user_id'])

    if not user.get().exists:
        user_data = {
            'email': user_token['email'],
            'id': user_token['user_id'],
        }
        firestore_db.collection('users').document(user_token['user_id']).set(user_data)

    users = firestore_db.collection('users').stream()

    return user


# Returns a list of all users in the firestore database
# Used for sharing files amongst users
def get_all_users(user_token) -> list:
    users = firestore_db.collection('users').stream()
    # convert the users to a list
    users_list = []
    for user in users:
        users_list.append(user.to_dict())

    # remove the user who is currently logged in
    for user in users_list:
        if user['id'] == user_token['user_id']:
            users_list.remove(user)
            break

    return users_list


# Assert the validity of the firebase token
def validate_firebase_token(id_token) -> Mapping[str, Any] | None:
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
