# Standard
from collections import defaultdict
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

class AuthToken:

    def __init__(self, db, resource_id):
        self.db = db 
        self.resource_id = resource_id
        self.timeout = TIMEOUT
        self.result = False
        self.done = False
        self.count = 0

    def reset(self):
        self.timeout = TIMEOUT
        self.count = 0

    def check(self, users):
        if users_are_authorized(self.db, users, self.resource_id):
            self.count += 1
            if self.count >= AUTH_THRESHOLD:
                self.result = True  # successful authorization
                self.done = True  
                
        self.timeout -= 1  # consumed 1 chance to authenticate

        if self.timeout == 0:
            self.done = True  # timed out

def everybody_in_video_is_authorized(db, kc, resource_id):
    token = AuthToken(db, resource_id)
    num_faces = 0

    while not token.done:
        faces = kc.get_faces_in_video()

        if num_faces != len(faces):
            # There's been a change in the number of people on screen
            token.reset()
            num_faces = len(faces)

        log_auth_attempt(token.timeout, token.count, num_faces)

        users = get_users_from_faces(db, faces)

        token.check(users)
            
    db.log_access_attempt(users, resource_id, token.result)
    return token.result

def access_handler(db, kc, resource_id):
    faces = kc.get_faces_in_video()
    initial_users = set(get_users_from_faces(db, faces))
    unattended = False
    unattended_count = 0
    new_user_appearances = defaultdict(int)
    NEW_USER_APPEARANCE_THRESHOLD = 5

    while resource_is_unlocked():
        faces = kc.get_faces_in_video()

        if faces:
            unattended = False
            unattended_count = 0
            new_users = set(get_users_from_faces(db, faces)) - initial_users
            for user in new_users:
                new_user_appearances[user] += 1
                if new_user_appearances[user] == NEW_USER_APPEARANCE_THRESHOLD:
                    # We can say with confidence that someone new has joined the party
                    # TODO make this singular
                    authorized = users_are_authorized(db, new_users, resource_id)
                    db.log_new_users_appearance(new_users, resource_id, authorized)

        elif unattended:
            if (time.time() -  start_time) > MAX_OPEN_TIME:
                # Left unattended for too long, send alert
                db.log_resource_time_out(resource_id)
                start_time = time.time()  # restart timer
        elif unattended_count > 5:
            # Now it is unattended, since we didn't see anyone on camera
            print('UNATTENDED!!!')
            unattended = True  
            start_time = time.time()  # start timer
        else:
            print("increment unattended count")
            unattended_count += 1
    

    db.log_resource_close(resource_id)

def getenv(var_name):
    # Get the value of an environment variable
    val = os.getenv(var_name)
    if val is None:
        raise ValueError(f"environment variable '{var_name}' not set")
    return val


def run_main_auth_routine():
    resource_id = getenv('CHOC_O_LOCK_RESOURCE_ID')
    aws_stream_name = getenv('AWS_VIDEO_STREAM_NAME')

    print("Application starting...")
    print("Connecting to AWS...")

    kc = Consumer(aws_stream_name)

    print('Connecting to database...')

    with DBClient() as db:
        print("Attempting to authorize...")
        if everybody_in_video_is_authorized(db, kc, resource_id):
            print('AUTHORIZED: you may enter the data center')
            unlock()
            access_handler(db, kc, resource_id)
        else:
            print('UNAUTHORIZED: Access Denied')


if __name__ == "__main__":
    run_main_auth_routine()
