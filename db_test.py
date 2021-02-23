from database import DBClient

with DBClient() as db:
    new_user = db.add_user('Morgan', 'Stark')
    print(f'User {new_user.first_name} {new_user.last_name} {new_user.id} added')
    print('Success')
