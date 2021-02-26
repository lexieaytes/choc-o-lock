from datetime import datetime, timezone
from uuid import uuid4

from classes import Resource, Unknown, User
from logger import logger


# *****************************
# ******* Mock Database *******
# *****************************
mock_user_table = {
    # UUID/user_id : User
    '3d2cf3ab-3beb-43e2-8065-86d4e0f99035': User('Tony', 'Stark', '3d2cf3ab-3beb-43e2-8065-86d4e0f99035'),
    '831a6f82-3e4b-4e84-98f7-bc116b77e822': User('Arya', 'Stark', '831a6f82-3e4b-4e84-98f7-bc116b77e822'),
    '589ae695-36de-4993-8470-e142cf111c6a': User('Robb', 'Stark', '589ae695-36de-4993-8470-e142cf111c6a')
}

mock_resource_table = {
    # resource_id : Resource
    1: Resource('Data Center 1', 'Data Center'),
    2: Resource('Rack 1', 'Rack'),
    3: Resource('Rack 2', 'Rack')
}

mock_auth_table = [
    # user_id : resource_id
    # If an entry is present, then that user is authorized to access that resource
    ('831a6f82-3e4b-4e84-98f7-bc116b77e822', '1'),
    ('831a6f82-3e4b-4e84-98f7-bc116b77e822', '2'),
    ('3d2cf3ab-3beb-43e2-8065-86d4e0f99035', '1'),
    ('3d2cf3ab-3beb-43e2-8065-86d4e0f99035', '3'),
    ('589ae695-36de-4993-8470-e142cf111c6a', '1')
]


class DBClient:

    def __init__(self):
        # TODO Initialization code goes here
        pass

    def __enter__(self):
        # TODO Database connection code goes here
        return self

    def __exit__(self, type, value, traceback):
        # TODO Database closing code goes here
        pass

    def add_user(self, first_name, last_name):
        # This should take in any values needed to create a new user in the database
        # and it should return a newly created User object
        #
        # We'll need to generate a User Id (UUID) to be the primary key for each new user
        # That should be done by the database (example format above in mock database)
        # We can reuse the same UUID for AWS Rekognition
        new_user_id = str(uuid4())
        # Now add the new user to our mock database
        new_user = User(first_name, last_name, new_user_id)
        mock_user_table[new_user_id] = new_user
        return new_user

    def get_user(self, user_id):
        # This should return a User object instantiated with the results from the database lookup
        # ex: (first name, last name, birthday, etc)
        # Note: we can add more fields to the User object above as needed
        return mock_user_table[user_id]

    def user_has_access_to_resource(self, user_id, resource_id):
        # Check if a user is authorized to access the given resource
        # This should return True if the user is authorized to access the resource
        # and return False otherwise
        for u_id, r_id in mock_auth_table:
            if u_id == user_id and r_id == resource_id:
                return True
        return False

    def log_access_attempt(self, users, resource_id, authorized):
        # :param users          list of User objects
        # :param resource_id    integer representing the resource Id in the database
        # :param authorized     True or False if all users are authorized
        #
        # Some general database ideas:
        #
        # ***** Access_log_table *****
        # Access_Id (primary key)
        # Time
        # Authorized
        # Resource_Id (foreign key to Resource table)
        # Unknown_user_count (how many unrecognized faces were on screen)
        #
        # ***** User_access_attempt_table *****
        # User_Id (foreign key to User table)
        # Access_Id (foreign key to Access_log_table)
        #
        unknown_user_count = len([user for user in users if user is Unknown])
        recognized_users = [user.id for user in users if user is not Unknown]
        logger.debug('-------- ACCESS ATTEMPT --------')
        logger.debug(f'Authorized: {authorized}')
        logger.debug(f'Resource Id: {resource_id}')
        logger.debug(f'Unknown Users: {unknown_user_count}')
        logger.debug(f'Recognized Users: {" ".join(recognized_users)}')
        logger.debug('--------------------------------')

    def log_resource_close(self, users, resource_id):
        unknown_user_count = len([user for user in users if user is Unknown])
        recognized_users = [user.id for user in users if user is not Unknown]
        logger.debug('-------- RESOURCE CLOSED --------')
        logger.debug(f'Resource Id: {resource_id}')
        logger.debug(f'Unknown Users: {unknown_user_count}')
        logger.debug(f'Recognized Users: {" ".join(recognized_users)}')
        logger.debug('--------------------------------')

    def log_resource_time_out(self, resource_id):
        logger.warning('!!! UNATTENDED ALERT !!!')
        logger.warning(f'Resource Timed Out: {resource_id}')

    def log_new_user_appearance(self, user, resource_id, authorized):
        logger.warning('-------- NEW APPEARANCE --------')
        logger.warning(f'Authorized: {authorized}')
        logger.warning(f'Resource Id: {resource_id}')
        logger.warning(f'Recognized User: {user.first_name} {user.last_name} {user.id}')
        logger.warning('--------------------------------')

    def log_unknown_user_appearance(self, num_unknown_users, resource_id):
        logger.warning('-------- UNKNOWN USER APPEARANCE --------')
        logger.warning(f'Resource Id: {resource_id}')
        logger.warning(f'Count: {num_unknown_users}')
        logger.warning('-----------------------------------------')
