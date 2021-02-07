# Standard
import os
import time

# Local
from aws_consumer import *
from database import *
from lock import *

TIMEOUT = 10
AUTH_THRESHOLD = 5
MAX_OPEN_TIME = 5


def get_user_from_face(db, face):
    matched_faces = face['MatchedFaces']

    if not matched_faces:
        # Face didn't match any known users
        return Unknown

    top_match = matched_faces[0]
    user_id = top_match['Face']['ExternalImageId']
    user = db.get_user(user_id)
    print(f'Recognized: {user.first_name} {user.last_name} | Similarity: {top_match["Similarity"]}')
    return user

def get_users_from_faces(db, faces):
    return [get_user_from_face(db, face) for face in faces]

def user_is_authorized(db, user, resource_id):
    if user is Unknown:
        print('Unknown person in video')
        return False

    return db.user_has_access_to_resource(user.id, resource_id)

def users_are_authorized(db, users, resource_id):
    if not users:
        print('Nobody detected')
        return False

    for user in users:
        if not user_is_authorized(db, user, resource_id):
            # Found an unauthorized person
            return False

    # Everybody on screen is authorized
    return True

def log_auth_attempt(timeout, auth_count, num_faces):
    print('-----------------------------')
    print('Timeout:', timeout)
    print('Auth count:', auth_count)
    print('Num faces:', num_faces)

def everybody_in_video_is_authorized(db, resource_id, aws_stream_name):
    timeout = TIMEOUT
    auth_count = 0
    num_faces = 0

    kc = Consumer(aws_stream_name)

    while timeout > 0:
        faces = kc.get_faces_in_video()

        if num_faces != len(faces):
            # There's been a change in the number of people on screen
            timeout = TIMEOUT  # reset timeout
            auth_count = 0
            num_faces = len(faces)

        log_auth_attempt(timeout, auth_count, num_faces)

        users = get_users_from_faces(db, faces)

        if users_are_authorized(db, users, resource_id):
            auth_count += 1
        else:
            auth_count = 0

        if auth_count > AUTH_THRESHOLD:
            db.log_access_attempt(users, resource_id, True)
            return True

        timeout -= 1  # consumed 1 chance to authenticate

    db.log_access_attempt(users, resource_id, False)
    return False

def access_handler(db, resource_id, stream_name):
    kc = Consumer(aws_stream_name)

    faces = kc.get_faces_in_video()
    curr_users = set(get_users_from_faces(db, faces))
    unattended = False

    while resource_is_unlocked():
        faces = kc.get_faces_in_video()

        if faces:
            unattended = False
            new_users = set(get_users_from_faces(db, faces))
            new_users = new_users - curr_users
            if new_users:
                # Someone new has joined the party
                authorized = users_are_authorized(db, new_users, resource_id)
                db.log_new_users_appearance(new_users, resource_id, authorized)
                curr_users |= new_users 
        elif not unattended:
            # Now it is unattended, since we didn't see anyone on camera
            print('UNATTENDED!!!')
            unattended = True  
            start_time = time.time()  # start timer
        elif (time.time() -  start_time) > MAX_OPEN_TIME:
            # Left unattended for too long, send alert
            db.log_resource_time_out(resource_id)
            start_time = time.time()  # restart timer

    db.log_resource_close(resource_id)

def getenv(var_name):
    # Get the value of an environment variable
    val = os.getenv(var_name)
    if val is None:
        raise ValueError(f"environment variable '{var_name}' not set")
    return val


if __name__ == "__main__":
    resource_id = getenv('CHOC_O_LOCK_RESOURCE_ID')
    aws_stream_name = getenv('AWS_VIDEO_STREAM_NAME')

    print("Application starting...")
    print('Connecting to database...')

    with DBClient() as db:
        print("Attempting to authorize...")
        if everybody_in_video_is_authorized(db, resource_id, aws_stream_name):
            print('AUTHORIZED: you may enter the data center')
            unlock()
            access_handler(db, resource_id, aws_stream_name)
        else:
            print('UNAUTHORIZED: Access Denied')
