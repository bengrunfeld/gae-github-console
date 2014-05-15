"""
Logs should be created for any action that causes a significant change.

Logs are stored in ndb and can be sorted by date and time, and send to specific
email addresses.
"""

import json
import os
import sys
import webapp2

sys.path.append('lib')

from datetime import datetime
from datetime import timedelta
from google.appengine.api import mail
from validate_email import validate_email

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
    log.put()


def show_all_logs():
    """Display a limited number of unfiltered logs to the user"""

    qry = Log.all()
    qry.order('-input_datetime')

    result = []

    for q in qry.run(limit=10):
        result.append(str(q.input_datetime) + ' ' + q.content)

    return result


def show_filtered_logs(from_date, to_date):
    """Retrieve logs from the datastore filtered by datetime"""

    qry = Log.all()

    # Filter based on if the values exist
    if from_date:
        qry.filter('input_datetime >', from_date)

    if to_date:
        qry.filter('input_datetime <', to_date)

    qry.order('-input_datetime')

    result = []

    for q in qry.run():
        result.append(' '.join([str(q.input_datetime), q.content]))

    return result


def format_logs(logs):
    """Place newline characters at the end of each line"""

    return '\n'.join(map(str, logs))


def send_email(user_address, logs):
    """Send a filtered list of logs to a specified email address"""

    sender_address = 'Github Console <no-reply@webfilings.com>'
    subject = 'Github Console Logs'

    # Indicate to the app if the mail was sent successfully or not
    if mail.send_mail(sender_address, user_address, subject, logs):
        return True

    return False


class DisplayLogs(webapp2.RequestHandler):
    """Display a time-specific list of logs"""

    def post(self):

        # Grab values from Logs filtering form
        from_date = json.loads(self.request.get('from_date'))
        to_date = json.loads(self.request.get('to_date'))

        # If both dates are false, show all logs and bail.
        if not check_dates(from_date, to_date):
            response = json.dumps(show_all_logs())
            self.response.out.write(response)
            return

        # Construct a datetime object, if the value isn't false
        from_date = _construct_datetime(from_date)
        to_date = _construct_datetime(to_date)

        # Filter logs by datetime and send results to the page
        response = json.dumps(show_filtered_logs(from_date, to_date))
        self.response.out.write(response)


class EmailLogs(webapp2.RequestHandler):
    """Email a time-specific list of logs to a certain email address"""

    def post(self):

        user_addresses = self.request.get('addresses')
        logs = json.loads(self.request.get('logs'))

        # Validate the email address
        # Check SMTP server by adding `check_mx=True`
        # Verify that email exists by adding `verify=True`
        if not validate_email(user_addresses):
            self.response.out.write('invalid')
            return

        # Format logs so that they contain newline characters
        formatted_logs = format_logs(logs)

        # If email logs is successful, send success message to user
        send_email(user_addresses, formatted_logs)

        self.response.out.write('success')


class LogDigest(webapp2.RequestHandler):
    """Send a daily digest of logs to a set email address"""

    def get(self):

        # Retrieve logs that are +/- 12 hrs from now for a 24 hr time period
        logs = show_filtered_logs((datetime.now - timedelta(hours=12)),
                                  (datetime.now + timedelta(hours=12)))

        # Format logs so that they contain newline characters
        formatted_logs = format_logs(logs)

        send_email(os.environ.get('ADMIN_EMAIL', formatted_logs))
