import logging
import mysql.connector


from datetime import datetime, timezone

from classes import Resource, Unknown, User

logger = logging.getLogger('choco')


# *****************************
# ******* Mock Database *******
# *****************************
mock_user_table = {
    # UUID/user_id : User
    '123': User('John', 'Jenny', '123'),
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
        self.conn = None
        self.cursor = None

#You may have to change the host and user info depending on where the database is located.
    def __enter__(self):
        self.conn = mysql.connector.connect(
	    user='admin',
	    password='admin',
            host='192.168.200.49',
            database='seniordesign',)

        self.cursor = self.conn.cursor(buffered=True)
        return self

    def __exit__(self, type, value, traceback):
        self.conn.close()

    def add_user(self, first_name, last_name):
        sql = """INSERT INTO SeniorDesign.dbo.employee(employeeFirstName, employeeLastName)
                 OUTPUT inserted.employeeID
                 VALUES (?, ?)"""

        self.cursor.execute(sql, first_name, last_name)
        user_id = self.cursor.fetchval()
        self.conn.commit()
        return User(first_name, last_name, user_id)

    def get_user(self, user_id):
        self.cursor.execute("SELECT * FROM SeniorDesign.dbo.employee WHERE employeeID = ?", user_id)
        row = self.cursor.fetchone()
        if row is None:
            raise ValueError(f'User {user_id} does not exist in the database')
        else:
            return User(row.first_name, row.last_name, row.id)

    def user_has_access_to_resource(self, user_id, resource_id):
        sql = "SELECT * FROM SeniorDesign.dbo.Permissions WHERE user_id = ? AND resource_id = ?"
        self.cursor.execute(sql, user_id, resource_id)
        row = self.cursor.fetchone()
        if row is None:
            return False  # record does not exist, so user does not have access
        else:
            return True

    def log_access_attempt(self, users, resource_id, authorized):
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
