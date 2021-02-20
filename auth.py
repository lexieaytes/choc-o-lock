from classes import Unknown


def log_auth_attempt(timeout, auth_count, num_users):
    print('-----------------------------')
    print('Timeout:', timeout)
    print('Auth count:', auth_count)
    print('Num users:', num_users)


def user_is_authorized(db, user, resource_id):
    if user is Unknown:
        print('Unknown user detected')
        return False

    return db.user_has_access_to_resource(user.id, resource_id)


def users_are_authorized(db, users, resource_id):
    if not users:
        print('Nobody detected')
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
