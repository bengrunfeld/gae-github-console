from google.appengine.ext import ndb


class Log(ndb.Model):
    """Models an individual log with a datetime property and log content"""
    datetime = ndb.DateTimeProperty(auto_now_add=True)
    content = ndb.StringProperty()
