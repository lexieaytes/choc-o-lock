# TODO: update to real lock interface
def unlock():
    print('Unlocking...')

# TODO: update to real lock interface
def resource_is_unlocked():
    with open('lock.lock') as lock:
        status = int(lock.read().strip('\n'))
        return status