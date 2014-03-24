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
import jinja2

from google.appengine.api import users, urlfetch
from basehandler import BaseHandler


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class GithubAuth(BaseHandler):

    def auth_admin(self):
        """Authenticate that user is an admin of the organization"""

        code = 'code'
        url = ''
        access_token = ''
        is_admin_of_wf = False
        result = ''

        # If admin not logged in to Google Accounts, take them to login page
        google_user = users.get_current_user()

        if google_user:
            url = self.request.url
            if code not in url:
                # Redirect to GH for code
                url = 'https://github.com/login/oauth/authorize? \
                    scope=user,repo&client_id=' \
                    + os.environ.get('CLIENT_ID')

                self.redirect(url)
            else:
                # User has been to GH, continue with auth process.
                cutoff = url.find('=')
                cutoff += 1
                code = url[cutoff:]

                # We have code, now get Access Token
                fields = {
                    "client_id": os.environ.get('CLIENT_ID'),
                    "client_secret": os.environ.get('CLIENT_SECRET'),
                    "code": code
                }
                url = 'https://github.com/login/oauth/access_token'
                data = urllib.urlencode(fields)
                result = urlfetch.fetch(url=url,
                                        payload=data,
                                        method=urlfetch.POST
                                        )

                # Get the query string
                query_string = str(result.content)

                # Get the access token out of the full query string
                access_token = query_string[13:]
                end_access = access_token.find('&')
                access_token = access_token[:end_access]

                # Check if user is an admin of WebFilings
                # still need to add admin test
                url = 'https://api.github.com/user/orgs?access_token=' \
                    + str(access_token)

                result = urlfetch.fetch(
                    url=url,
                    method=urlfetch.GET,
                )

                orgs = json.loads(result.content)

                for org in orgs:
                    if 'login' in org and org['login']:
                        if org['login'] == os.environ.get('ORG'):
                            is_admin_of_wf = True

                # If not admin, send to 403
                if not is_admin_of_wf:
                    self.redirect('/403')
                else:
                    # User is admin of WebFilings,
                    # return access token to calling class
                    return access_token

    def auth_user(self):
        """Authenticate that user belongs to the organization"""

        code = 'code'
        url = ''
        access_token = ''
        is_user_of_wf = False
        result = ''

        # If user not logged in to Google Accounts, take them to login page
        google_user = users.get_current_user()

        if google_user:
            url = self.request.url
            if code not in url:
                # Redirect to GH for code
                url = 'https://github.com/login/oauth/authorize? \
                    scope=user,repo&client_id=' + os.environ.get('CLIENT_ID')
                self.redirect(url)
            else:
                # User has been to GH, continue with auth process.
                cutoff = url.find('=')
                cutoff += 1
                code = url[cutoff:]

                # We have code, now get Access Token
                fields = {
                    "client_id": os.environ.get('CLIENT_ID'),
                    "client_secret": os.environ.get('CLIENT_SECRET'),
                    "code": code
                }
                url = 'https://github.com/login/oauth/access_token'
                data = urllib.urlencode(fields)
                result = urlfetch.fetch(url=url,
                                        payload=data,
                                        method=urlfetch.POST
                                        )

                # Get the query string
                query_string = str(result.content)

                # Get the access token out of the full query string
                access_token = query_string[13:]
                end_access = access_token.find('&')
                access_token = access_token[:end_access]

                # Check if user belongs to WebFilings
                url = 'https://api.github.com/user/orgs?access_token=' \
                    + str(access_token)

                result = urlfetch.fetch(
                    url=url,
                    method=urlfetch.GET,
                )

                orgs = json.loads(result.content)

                for org in orgs:
                    if 'login' in org and org['login']:
                        if org['login'] == os.environ.get('ORG'):
                            is_user_of_wf = True

                # If not admin, send to 403
                if not is_user_of_wf:
                    self.redirect('/403')
                else:
                    # User is admin of WebFilings,
                    # return access token to calling class
                    self.session['access_token'] = access_token
                    self.redirect('/')
