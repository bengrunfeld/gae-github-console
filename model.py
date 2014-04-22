"""
The model that the Credentials object uses to store and retrieve the access
token from the datastore.
"""

from google.appengine.ext import db
from oauth2client.appengine import CredentialsProperty


class CredentialsModel(db.Model):
    credentials = CredentialsProperty()


class Log(db.Model):
    """Models a log entry which is created for every significant user action"""
    datetime = db.DateTimeProperty(auto_now_add=True)
    content = db.StringProperty(required=True)
