"""
Render the front end of the app
"""

import os
import webapp2
import json

from google.appengine.api import urlfetch

from auth import get_access_token
from auth import fetch_url
from basehandler import BaseHandler
from config import config

def _get_front_page_data():
    """Retrieve list of private repos for the org"""
    
    # Set the url to retrieve all the private repos for an org
    url = 'https://api.github.com/orgs/{}/repos?access_token={}'.format(
            os.environ.get('ORG'), get_access_token()) 

    # Fetch the list of private repos
    content = json.loads(fetch_url(url))

    response = [] 

    # Retrieve the repo names from the JSON response
    for value in content:
        response.append(value.get('name'))

    return response


class RenderApp(BaseHandler):
    """
    Check that the user is logged in, then render the front end of the app
    """
    
    def get(self):

        # Check that user is logged in. Send to auth if False
        if not self.session.get('logged_in'):
            self.redirect('/auth')
            return

        # Get data for render
        data = _get_front_page_data()

        # Put data into context
        context = {"repos": data}
    
        # Render the app
        self.render('index', context)


config = config() 

app = webapp2.WSGIApplication([
    ('/app', RenderApp),
], config=config, debug=True)
