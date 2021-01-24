# Standard
from datetime import datetime, timezone
from uuid import uuid4


class User:
    def __init__(self, first_name, last_name, user_id):
        self.first_name = first_name
        self.last_name = last_name
        self.id = user_id

class Resource:
        def __init__(self, name, resource_type):
            self.name = name
            self.type = resource_type  # Data Center or Server Rack


mock_user_table = {
    # UUID/user_id : User
    '3d2cf3ab-3beb-43e2-8065-86d4e0f99035': User('Ned', 'Bigby', '3d2cf3ab-3beb-43e2-8065-86d4e0f99035'),
    '831a6f82-3e4b-4e84-98f7-bc116b77e822': User('Suzie', 'Crabgrass', '831a6f82-3e4b-4e84-98f7-bc116b77e822')
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
    ('3d2cf3ab-3beb-43e2-8065-86d4e0f99035', '3')
]


# TODO: connect to real database
def get_user_from_db(user_id):
    # This should return a User object with values from database
    # ex: (first name, last name, birthday, etc)
    # Note: we can add more fields to the User object above
    return mock_user_table[user_id]

# TODO: connect to real database
def user_has_access_to_resource(user_id, resource_id):
    # Check if a user is authorized to access the given resource
    # This function should return True if the user is authorized to access the resource
    # and return False otherwise
    for u_id, r_id in mock_auth_table:
        if u_id == user_id and r_id == resource_id:
            return True
    return False

# TODO: connect to real database
def log_access_attempt_to_db(users_on_screen, resource_id, authorized):
    # :param users_on_screen will contain a list of User objects
    # However, some users might just be the string "Unknown"
    # ex: [<User1>, <User2>, 'Unknown', <User4>]

    # Some ideas:
    # We'll need a main access log table
    # Example:
    # ***** Access_log_table *****
    # Access_Id (primary key)
    # Time
    # Authorized
    # Resource_Id (foreign key to Resource table)
    # Unknown_user_count (how many unrecognized faces were on screen)

    # And a table to join authenticated users
    # Example:
    # ***** User_access_attempt_table *****
    # User_Id (foreign key to User table)
    # Access_Id (foreign key to Access_log_table)
    unknown_user_count = len([user for user in users_on_screen if user == 'Unknown'])
    recognized_users = [user.id for user in users_on_screen if user != 'Unknown']
    print('---------- ACCESS ATTEMPT ----------')
    print(f'Time: {datetime.now(timezone.utc)}')
    print(f'Authorized: {authorized}')
    print(f'Resource Id: {resource_id}')
    print(f'Unknown Users: {unknown_user_count}')
    print(f'Recognized Users: {" ".join(recognized_users)}')
    print('------------------------------------')

# TODO: connect to real database
def log_resource_close_to_db(resource_id):
    # This logs that the resource is closed (locked)
    print(f'Resource Closed: {resource_id}')

# TODO: connect to real database
def log_resource_time_out_to_db(resource_id):
    # This logs that the resource has been open for more than the predetermined time
    print(f'Resource Timed Out: {resource_id}')

# TODO: connect to real database
def add_user_to_db(first_name, last_name):
    # This should take in any values needed to create a new user for the database
    # And return a newly created User object

    # Need to generate a new User Id (UUID)
    # This should be the primary key for the user
    # Ultimately, the UUID should be generated by the database
    # We'll use the same UUID for AWS Rekognition
    new_user_id = str(uuid4())
    # Now add the new user to our mock database
    new_user = User(first_name, last_name, new_user_id)
    mock_user_table[new_user_id] = new_user
    return new_user
