"""
Retrieve an access token for a Github User

Use the Google Flow workflow to walk through each stage of the OAuth 2.0
process.
"""

import os
import sys
import webapp2

from urlparse import urlparse
from urlparse import parse_qs

from google.appengine.api import urlfetch

sys.path.append("lib")

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.appengine import StorageByKeyName

from model import CredentialsModel
from basehandler import BaseHandler


GITHUB_ORGS_MEMBER_URL = 'https://api.github.com/user/orgs'
GITHUB_API_URL = 'https://api.github.com'


def create_flow_object():
    """Check if client_secrets.json is populated"""

    flow = flow_from_clientsecrets('./client_secrets.json',
                                   'user,repo',
                                   'http://localhost:8080/code')
    return flow


def get_auth_uri(flow):
    """Provide the API keys and receive a temporary code in return"""

    OAuth2WebServerFlow(client_id=flow.client_id,
                        client_secret=flow.client_secret,
                        scope=flow.scope,
                        redirect_uri=flow.redirect_uri)

    auth_uri = flow.step1_get_authorize_url()

    return auth_uri


def get_access_token():
    """Used to check app activation and append token to urls"""

    # Check if access token is in storage
    storage = StorageByKeyName(CredentialsModel, 'token', 'credentials')

    credentials = storage.get()

    if not credentials:
        return False

    return credentials.access_token


def delete_access_token():
    """Delete access token from storage"""

    storage = StorageByKeyName(CredentialsModel, 'token', 'credentials')
    storage.delete()


def retrieve_code(url):
    """Retrieve code from url"""

    parsed_url = parse_qs(urlparse(url).query)
    code = parsed_url['code'][0]
    return code


def get_org_name():
    """Return the ORG environment variable"""

    return os.environ.get('ORG')


def user_is_org_member():
    """Check that user has org listed in their org memberships list"""

    url = '{}?access_token={}'.format(GITHUB_ORGS_MEMBER_URL,
                                      get_access_token())

    result = urlfetch.fetch(url=url, method=urlfetch.GET)

    if not '"login":"WebFilings"' in result.content:
        return False

    return True


def user_is_org_admin():
    """Check that user belongs to owners team in org"""

    url = '{}/orgs/{}/teams?access_token={}'.format(GITHUB_API_URL,
                                                    get_org_name(),
                                                    get_access_token())

    result = urlfetch.fetch(url)

    # Check if user belongs to the Owners team
    if not '"name":"Owners"' in result.content:
        delete_access_token()
        return False

    return True


class DetectActivation(BaseHandler):
    """Detect if the app is set up"""

    def get(self):

        if not get_access_token():
            # App is not set up
            print('No access token')
            self.redirect('/auth')
            return

        if not self.session.get('logged_in'):
            # User is not logged in
            self.redirect('/auth')
            return

        # Everything checks out, send user to auth
        self.redirect('/app')


class AuthUser(webapp2.RequestHandler):
    """Auth user via the Github API"""

    def get(self):

        # Begin Google's flow workflow
        flow = create_flow_object()

        if not flow:
            self.error(404)
            return

        # Use the flow object to construct an authorization uri
        auth_uri = str(get_auth_uri(flow))

        if not auth_uri:
            self.error(404)
            return

        self.redirect(auth_uri)
        return


class RetrieveToken(BaseHandler):
    """Switch the temporary code for an access token"""

    def get(self):

        if get_access_token():
            # App is set up, we just want to check if user belongs to org
            if not user_is_org_member():
                print('User is not org member')
                self.render('403')
                self.error(403)
                return
            else:
                # User is now logged in, send to app
                print('User is an org member, send them to app')
                self.session['logged_in'] = True
                self.redirect('/app')
                return

        # Get the code out of the url
        code = retrieve_code(self.request.url)

        # Create a Credentials object which will hold the access token
        flow = create_flow_object()
        credentials = flow.step2_exchange(code)

        # Store the access token, app is now activated
        storage = StorageByKeyName(CredentialsModel, 'token', 'credentials')
        storage.put(credentials)

        if not user_is_org_admin():
            print('User is not an org admin')
            self.error(403)
            self.render('not_admin')
            return

        # User is logged in
        self.session['logged_in'] = True

        context = {
            "access_token": credentials.access_token,
            "username": "admin",
        }

        # Render token
        self.render('login', context)


class DeleteSessionsAndDb(BaseHandler):
    """Delete all session vars and the access token in the db"""

    def get(self):

        # Kill all session data
        self.session.clear()

        # Store the access token, app is now activated
        delete_access_token()

        print('All data deleted')


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': ''  # use secret key
}

application = webapp2.WSGIApplication([
    ('/', DetectActivation),
    ('/auth', AuthUser),
    ('/code', RetrieveToken),
    ('/del', DeleteSessionsAndDb),
], config=config, debug=True)
