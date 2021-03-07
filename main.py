import argparse
import logging
import os

from access import AccessToken
from auth import AuthToken
from classes import *
from consumer import *
from database import *
from lock import *
from logger import logger
from setup import already_setup, get_stream_name, setup

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


def access_handler(db, kc, resource_id, users):
    unlock()

    token = AccessToken(db, resource_id, users, 
                        TIME_UNTIL_UNATTENDED_ALERT, UNKNOWN_USER_THRESHOLD)

    while resource_is_unlocked():
        users = get_users_in_video(db, kc)
        token.check(users)

    db.log_resource_close(users, resource_id)
    print('Resource Closed')


def main(resource_id):
    if not already_setup():
        print('Running setup...')
        setup()
    else:
        print('Already setup, skipping...')

    aws_stream_name = get_stream_name()

    print("Connecting to Kinesis Data Stream...")

    kc = Consumer(aws_stream_name)

    print('Connecting to database...')

    with DBClient() as db:
        print("Attempting to authorize...")
        auth_handler(db, kc, resource_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Choc-o-Lock Security System')
    parser.add_argument('--resource-id', required=True, help='ID of the resource (data center or server rack)')
    parser.add_argument('--debug', action='store_true', help='Run in DEBUG mode')
    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    main(args.resource_id)
