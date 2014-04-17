"""
Create a new private repo belonging to the organization
"""

import os
import webapp2
import json

from google.appengine.api import urlfetch

from auth import fetch_url
from auth import get_access_token
from basehandler import BaseHandler


def _create_private_repo(name, description, private=True):
    """Create a private repo"""

    url = 'https://api.github.com/orgs/{}/repos?access_token={}'.format(
            os.environ.get('ORG'), get_access_token())
    
    fields = {
        "name": name,
        "description": description,
        "private": True,
    }

    # Send request to Github's API
    result = fetch_url(url, urlfetch.POST, json.dumps(fields))
    return


def _create_log_entry():
    """Create a log entry for the creation of the private repo"""
    pass


class CreateRepo(BaseHandler):
    """Auth user and create a private repo"""

    def post(self):
        
        # Check user is logged in 
        if not self.session.get('logged_in'):
            self.redirect('/auth')

        # Send new repo data to create repo func
        _create_private_repo(self.request.get('repo-name'), 
                             self.request.get('repo-desc'))

        # Reload app
        self.redirect('/app')


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': ''  # use secret key
}

app = webapp2.WSGIApplication([
    ('/create-repo', CreateRepo),
], config=config, debug=True)
