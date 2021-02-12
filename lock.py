# TODO connect to the real lock
def unlock():
    print('Unlocking...')

# TODO connect to the real lock
def resource_is_unlocked():
    # Return True if the resource is unlocked
    # and False otherwise
    with open('lock.lock') as lock:
        status = int(lock.read().strip('\n'))
        return status