"""
Auth admins and users so that they may enter the product

The auth process retrieves the access token of the user
and prints it to the screen so that they may copy and
paste it to the app.yaml file. While not ideal, this workflow
is necessary since there is no way in GAE to set a reusable
environment variable, like in Heroku.

"""

import os
import json
import urllib
import uuid

from urlparse import parse_qs

from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api import users

import webapp2

from basehandler import BaseHandler

GITHUB_AUTH_URL = 'https://github.com/login/oauth/authorize'
GITHUB_ACCESS_URL = 'https://github.com/login/oauth/access_token'
GITHUB_ORGS_URL = 'https://api.github.com/user/orgs'
GITHUB_CHECK_USER = 'https://api.github.com/user'

# Get the redirect URLs for our own application.
APP_ROOT = 'http://{}'.format(os.environ['HTTP_HOST'])
GET_ACCESS_TOKEN_URL = '{}/get-access-token/'.format(APP_ROOT)
DISPLAY_ACCESS_TOKEN_URL = '{}/get-access-token/'.format(APP_ROOT)

# Get the Access Token, if it exists
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')


def _user_is_org_member(access_token):
    """Check if user is a member of ORG."""

    url = '{}?access_token={}'.format(GITHUB_ORGS_URL, access_token)
    result = urlfetch.fetch(url=url, method=urlfetch.GET)

    orgs = json.loads(result.content)

    for org in orgs:
        if org.get('login') == os.environ.get('ORG'):
            return True

    return False

def _user_is_org_admin(access_token):
    """Check if user is an admin of ORG"""
    pass

def _get_access_token(auth_code):
    """Get an access token from an auth token."""

    request_params = {
        'client_id': os.environ.get('CLIENT_ID'),
        'client_secret': os.environ.get('CLIENT_SECRET'),
        'code': auth_code,
        'redirect_uri': DISPLAY_ACCESS_TOKEN_URL
    }

    result = urlfetch.fetch(GITHUB_ACCESS_URL,
                            payload=urllib.urlencode(request_params),
                            method=urlfetch.POST)

    content = parse_qs(result.content)
    return content['access_token'][0]
    # return json.loads(result.content).get('access_token')


class GetAuthTokenHandler(webapp2.RequestHandler):
    """Get an auth token that you can switch for an access token."""

    def get(self):
        # If the user has not authed to Google, bail.
        if not users.get_current_user():
            # TODO: Maybe return a 403 here?
            self.error(403)
            return

        # TODO: Change this into a flow object
        state = uuid.uuid4().hex
        memcache.set(state, True, time=300)

        request_params = {
            'scope': 'user,repo',
            'client_id': os.environ.get('CLIENT_ID'),
            'redirect_uri': GET_ACCESS_TOKEN_URL,
            'state': state
        }
        url = '{}?{}'.format(GITHUB_AUTH_URL, urllib.urlencode(request_params))
        self.redirect(url)

class GetAccessTokenHandler(BaseHandler):
    """Convert the auth token supplied by github to an access token."""

    def get(self):
        # If the user has not authed to Google, bail.
        if not users.get_current_user():
            # TODO: Maybe return a 403 here?
            self.error(403)
            self.redirect('/403')
            return

        state = self.request.get('state')
        if not state or not memcache.get(state):
            # TODO: What to do here?
            self.error(403)
            return

        memcache.delete(state)

        code = self.request.get('code')
        if not code:
            # TODO: What to do here?
            self.error(500)
            return

        access_token = _get_access_token(code)

        if not _user_is_org_member(access_token):
             # TODO: Maybe this could be better?
            self.error(403)
            return

        if not os.environ.get('ACCESS_TOKEN'):
            # This means the app isn't set up.  Admin needs to do so.
            self.redirect(
                '/display_token?access_token={}'.format(access_token))
            return

        # TODO: Probably need to set the user name or something here.
        # TODO: This probably needs to inherit from BaseHandler for this to
        # work correctly.
        self.session['github_member'] = True
        self.redirect('/')
        return

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': os.environ.get('SESSION_SECRET'),
}

application = webapp2.WSGIApplication([
    ('/get-auth-token', GetAuthTokenHandler),
    ('/get-access-token/.*', GetAccessTokenHandler),
], config=config, debug=True)
