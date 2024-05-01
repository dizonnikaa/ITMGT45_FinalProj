import database

def login(username, password):
    user = database.get_user(username)
    if user and user['password'] == password:
        return True, user
    else:
        return False, None