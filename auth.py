from classes import Unknown
from logger import logger


def log_auth_attempt(timeout, auth_count, num_users):
    logger.debug(f'Timeout: {timeout}')
    logger.debug(f'Auth count: {auth_count}')
    logger.debug(f'Num users: {num_users}')
    logger.debug('-----------------------------')


def user_is_authorized(db, user, resource_id):
    if user is Unknown:
        logger.warning('Unknown user detected')
        return False

    return db.user_has_access_to_resource(user.id, resource_id)


def users_are_authorized(db, users, resource_id):
    if not users:
        logger.debug('Nobody detected')
        return False

    for user in users:
        if not user_is_authorized(db, user, resource_id):
            return False

    # Everybody on screen is authorized
    return True


class AuthToken:

    def __init__(self, db, resource_id, timeout, auth_threshold):
        self.db = db 
        self.resource_id = resource_id
        self.timeout_start = timeout
        self.timeout = timeout
        self.auth_threshold = auth_threshold
        self.authorized = False
        self.done = False
        self.count = 0
        self.num_users = 0

    def reset(self):
        self.timeout = self.timeout_start
        self.count = 0

    def check(self, users):
        if self.num_users != len(users):
            # The number of users on screen has changed
            self.reset()
            self.num_users = len(users)

        log_auth_attempt(self.timeout, self.count, self.num_users)

        if users_are_authorized(self.db, users, self.resource_id):
            self.count += 1
            if self.count >= self.auth_threshold:
                self.authorized = True 
                self.done = True 
                
        self.timeout -= 1  # consumed 1 chance 

        if self.timeout == 0:
            self.done = True 
