import os

from access import AccessToken
from auth import AuthToken
from classes import *
from consumer import *
from database import *
from lock import *

TIMEOUT = 10
AUTH_THRESHOLD = 4
TIME_UNTIL_UNATTENDED_ALERT = 10  # seconds
UNKNOWN_USER_THRESHOLD = 6
 

def auth_handler(db, kc, resource_id):
    token = AuthToken(db, resource_id, TIMEOUT, AUTH_THRESHOLD)

    while not token.done:
        users = get_users_in_video(db, kc)
        token.check(users)
            
    db.log_access_attempt(users, resource_id, token.authorized)

    if token.authorized:
        print('AUTHORIZED: You may enter the data center')
        access_handler(db, kc, resource_id, users)
    else:
        print('UNAUTHORIZED: Access Denied')


def access_handler(db, kc, resource_id, initial_users):
    unlock()

    token = AccessToken(db, resource_id, initial_users, 
                        TIME_UNTIL_UNATTENDED_ALERT, UNKNOWN_USER_THRESHOLD)

    while resource_is_unlocked():
        users = get_users_in_video(db, kc)
        token.check(users)

    db.log_resource_close(users, resource_id)


def getenv(var_name):
    # Get the value of an environment variable
    val = os.getenv(var_name)
    if val is None:
        raise ValueError(f"environment variable '{var_name}' not set")
    return val


def main():
    resource_id = getenv('CHOC_O_LOCK_RESOURCE_ID')
    aws_stream_name = getenv('AWS_VIDEO_STREAM_NAME')

    print("Connecting to AWS...")

    kc = Consumer(aws_stream_name)

    print('Connecting to database...')

    with DBClient() as db:
        print("Attempting to authorize...")
        auth_handler(db, kc, resource_id)


if __name__ == "__main__":
    main()
