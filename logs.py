"""
Logs should be created for any action that causes a significant change.

Logs are stored in ndb and can be sorted by date and time, and send to specific
email addresses.
"""

import os
import webapp2
import json

from datetime import datetime
from google.appengine.api import urlfetch
from google.appengine.ext import db

from basehandler import BaseHandler
from config import config
from model import Log


GITHUB_API_URL = 'https://api.github.com'


def check_dates(from_date, to_date):
    """Check dates to see if false or not"""

    if not from_date and not to_date:
        return False
    
    return True


def _construct_datetime(daterange):
    """Construct a datetime that will be used to create logs"""

    # If a datetime isn't set, bail
    if not daterange: 
        return

    # Can only grab values after var has been checked to be True
    dt = daterange['values']
    
    # Return a datetime object
    return datetime(dt[0], dt[1], dt[2], dt[3], dt[4]) 


def create_log(content):
    """Create a log for every user action made"""

    log = Log(content=content)
    log.put 


def show_all_logs():
    """Display a limited number of unfiltered logs to the user"""

    qry = Log.all()
    # result = qry.run(limit=30)
    # print(result)


class DisplayLogs(webapp2.RequestHandler):
    """Display a time-specific list of logs"""

    def post(self):

        # Grab values from Logs filtering form
        from_date = json.loads(self.request.get('from_date'))
        to_date = json.loads(self.request.get('to_date'))

        # If both dates are false, bail.
        if not check_dates(from_date, to_date):
            show_all_logs()
            return 

        # Construct a datetime object, if the value isn't false 
        from_date = _construct_datetime(from_date)
        to_date = _construct_datetime(to_date)

        print(from_date, to_date)
        

class EmailLogs(webapp2.RequestHandler):
    """Email a time-specific list of logs to a certain email address"""

    def post(self):
        pass


class LogDigest(webapp2.RequestHandler):
    """Send a daily digest of logs to a set email address"""

    def post(self):
        pass


config = config()

app = webapp2.WSGIApplication([
    ('/display-logs', DisplayLogs),
    ('/email-logs', EmailLogs),
    ('/digest-logs', LogDigest),
], config=config, debug=True)
