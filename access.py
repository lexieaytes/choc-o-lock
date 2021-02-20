import time

from auth import user_is_authorized
from classes import Unknown

class Timer:

    def __init__(self, time_interval):
        self.time_interval = time_interval
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    @property
    def is_expired(self):
        return self.start_time and time.time() - self.start_time > self.time_interval


class AccessToken:

    def __init__(self, db, resource_id, initial_users, alert_time, unknown_threshold):
        self.db = db
        self.resource_id = resource_id
        self.curr_users = set(initial_users)
        self.unattended = False
        self.unattended_timer = Timer(alert_time)
        self.unknown_threshold = unknown_threshold
        self.unknown_count = 0

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
            if user is Unknown:
                num_unknown_users += 1
            else:
                authorized = user_is_authorized(self.db, user, self.resource_id)
                self.db.log_new_user_appearance(user, self.resource_id, authorized)
                self.curr_users.add(user)
    
        print('Unknown users:', num_unknown_users)
        print('Count:', self.unknown_count)

        if num_unknown_users:
            self.unknown_count += 1
            if self.unknown_count == self.unknown_threshold:
                self.db.log_unknown_user_appearance(num_unknown_users, self.resource_id)
        else:
            # There were no unknown users
            self.unknown_count = 0