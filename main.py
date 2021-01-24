# Standard
import os
import time

# Third-party
from kinesis.consumer import KinesisConsumer

# Local
from database import *
from face_utils import *

TIMEOUT = 10
AUTH_THRESHOLD = 5
MAX_OPEN_TIME = 10

RESOURCE_ID = None
AWS_STREAM_NAME = None


def get_user_from_face(face):
    matched_faces = face['MatchedFaces']

    if not matched_faces:
        # Face didn't match any known users
        return 'Unknown'

    top_match = matched_faces[0]
    user_id = top_match['Face']['ExternalImageId']
    user = get_user_from_db(user_id)
    print(f'Recognized: {user.first_name} {user.last_name} | Similarity: {top_match["Similarity"]}')
    return user

def get_users_from_faces(faces):
    users = []
    for face in faces:
        user = get_user_from_face(face)
        users.append(user)
    return users

def user_is_authorized(user):
    if user == 'Unknown':
        print('Unknown person in video')
        return False

    return user_has_access_to_resource(user.id, RESOURCE_ID)

def users_are_authorized(users):
    if not users:
        print('Nobody detected')
        return False

    for user in users:
        if not user_is_authorized(user):
            # Found an unauthorized person
            return False

    # Everybody on screen is authorized
    return True

def video_stream():
    consumer = KinesisConsumer(stream_name=AWS_STREAM_NAME)
    for message in consumer:
        data = eval(message['Data'])
        faces = data['FaceSearchResponse']  # faces detected in video
        yield faces

def log_auth_attempt(timeout, auth_count, num_faces):
    print('---------------------------------')
    print('Timeout:', timeout)
    print('Auth count:', auth_count)
    print('Num faces:', num_faces)

def everybody_in_video_is_authorized():
    timeout = TIMEOUT
    auth_count = 0
    num_faces = 0

    for faces in video_stream():
        if num_faces != len(faces):
            # Change in number of faces on screen
            timeout = TIMEOUT  # reset timeout
            auth_count = 0
            num_faces = len(faces)

        log_auth_attempt(timeout, auth_count, num_faces)

        users = get_users_from_faces(faces)

        if users_are_authorized(users):
            auth_count += 1
        else:
            auth_count = 0

        if auth_count > AUTH_THRESHOLD:
            log_access_attempt_to_db(users, RESOURCE_ID, True)
            return True

        timeout -= 1  # consumed 1 chance to authenticate

        if timeout == 0:
            log_access_attempt_to_db(users, RESOURCE_ID, False)
            return False

def timer(resource_id):
    start_time = time.time()
    while is_unlocked():
        if (time.time() -  start_time) > MAX_OPEN_TIME:
            log_resource_time_out_to_db(resource_id)
            start_time = time.time()

def is_unlocked():
    # Checks if door is shut (locked)
    # TODO: replace this with real interface for lock
    try:
        time.sleep(1)
        return True
    except KeyboardInterrupt:
        return False

def door_handler(resource_id):
    timer(resource_id)
    log_resource_close_to_db(resource_id)

def getenv(var_name):
    # Get the value of an environment variable
    val = os.getenv(var_name)
    if not val:
        print(f'{var_name} environment variable not set')
        print('Exiting...')
        exit()
    return val


if __name__ == "__main__":
    RESOURCE_ID = getenv('CHOC_O_LOCK_RESOURCE_ID')
    AWS_STREAM_NAME = getenv('AWS_VIDEO_STREAM_NAME')

    print("Application starting...")
    print("Attempting to authorize...")
    if everybody_in_video_is_authorized():
        print('AUTHORIZED: you may enter the data center')
        door_handler(RESOURCE_ID)
    else:
        print('UNAUTHORIZED: Access Denied')
