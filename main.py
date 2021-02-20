import os
import time

from aws_consumer import *
from database import *
from lock import *

TIMEOUT = 10
AUTH_THRESHOLD = 4
UNKNOWN_USER_THRESHOLD = 6
TIME_UNTIL_UNATTENDED_ALERT = 10  # seconds


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
                self.result = True  # successfully authenticated
                self.done = True 
                
        self.timeout -= 1  # consumed 1 chance to authenticate

        if self.timeout == 0:
            self.done = True  

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

class Timer:

    def __init__(self, time_interval):
        self.time_interval = time_interval
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    @property
    def is_expired(self):
        return bool(self.start_time) and time.time() - self.start_time > self.time_interval

class AccessToken:

    def __init__(self, db, resource_id, initial_users):
        self.db = db
        self.resource_id = resource_id
        self.curr_users = set(initial_users)
        self.unknown_count = 0
        self.unattended = False
        self.unattended_timer = Timer(TIME_UNTIL_UNATTENDED_ALERT)

    def check(self, users):
        if users:
            self.unattended = False
            self.verify(users)
        elif not self.unattended:
            # Now we are unattended (at least for a moment)
            print('nobody on screen')
            self.unattended = True
            self.unattended_timer.start()
        elif self.unattended_timer.is_expired:
            # We've been unattended for too long
            print('!!! UNATTENDED ALERT !!!')
            self.db.log_resource_time_out(self.resource_id)
            self.unattended_timer.start()  # restart timer
        else:
            print('still unattended')

    def verify(self, users):
        new_users = set(users) - self.curr_users
        num_unknown_users = 0
        for user in new_users:
            if user is not Unknown:
                authorized = user_is_authorized(self.db, user, self.resource_id)
                self.db.log_new_user_appearance(user, self.resource_id, authorized)
                self.curr_users.add(user)
            else:
                num_unknown_users += 1

        print('Unknown users:', num_unknown_users)
        print('Count:', self.unknown_count)

        if num_unknown_users:
            self.unknown_count += 1
            if self.unknown_count == UNKNOWN_USER_THRESHOLD:
                self.db.log_unknown_user_appearance(num_unknown_users, self.resource_id)
        else:
            # There were no unknown users
            self.unknown_count = 0

def access_handler(db, kc, resource_id):
    faces = kc.get_faces_in_video()
    initial_users = get_users_from_faces(db, faces)
    token = AccessToken(db, resource_id, initial_users)

    while resource_is_unlocked():
        faces = kc.get_faces_in_video()
        users = get_users_from_faces(db, faces)
        token.check(users)

    db.log_resource_close(users, resource_id)

def getenv(var_name):
    # Get the value of an environment variable
    val = os.getenv(var_name)
    if val is None:
        raise ValueError(f"environment variable '{var_name}' not set")
    return val

def run_main_auth_routine():
    resource_id = getenv('CHOC_O_LOCK_RESOURCE_ID')
    aws_stream_name = getenv('AWS_VIDEO_STREAM_NAME')

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
