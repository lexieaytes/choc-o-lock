# Import modules
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
# Setup
relayPin = 21
GPIO.setmode(GPIO.BCM) # IMPORTANT: setting mode to either BCM or BOARD
GPIO.setup(relayPin, GPIO.OUT)
GPIO.output(relayPin, 0) # Initally locks the lock


# TODO: update to real lock interface
def unlock():
    print('Unlocking...')
    GPIO.output(relayPin, 1)

# TODO integrate with the real lock
def resource_is_unlocked():
    # Return True if the resource is unlocked
    # and False otherwise

    lock_state = GPIO.input(21)
    
    if lock_state == 1:
        print("Lock state is: ", lock_state)
        return True
    return False





    # with open('lock.lock') as lock:
    #     status = int(lock.read().strip('\n'))
    #     return status

