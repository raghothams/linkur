
from flask.ext.login import UserMixin
import uuid

class User(UserMixin):
    # EMAIL
    # PASSWORD
    # NAME
    # GROUPS (COPY)

    def __init__(self, email=None, password=None, name=None, id=None):
        self.id = id
        self.email = email
        self.password = password
        self.name = name

    def serialize(self):

        return {
            "_id" : str(self.id),
            "email" : self.email,
            "password" : self.password,
            "name" : self.name,
        }


#
#    this method should just return True unless the object represents 
#    a user that should not be allowed to authenticate for some reason.
#
    def is_authenticated(self):
        return True


#
#    this method should return True for users unless they are inactive, 
#    for example because they have been banned.
#
    def is_active(self):
        return True


#
#    this method should return True only for fake users that are not 
#    supposed to log in to the system.
#
    def is_anonymous(self):
        return False


#
#    this method should return a unique identifier for the user, in unicode format. 
#    We use the unique id generated by the database layer for this.
#
    def get_id(self):
        return unicode(self.id)

