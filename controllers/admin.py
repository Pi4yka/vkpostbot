import os

# check user_id in admin_id array
def getAdmin(user_id):
    check = False
    ADMIN_ID = os.getenv('ADMIN_ID')

    if (str(user_id) in ADMIN_ID):
        check = True
    
    return check

# add user_id in admin_id array
def setAdmin():
    return True