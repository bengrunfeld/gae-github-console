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
from config import config
from teams import get_all_teams
from teams import get_repo_teams
from teams import remove_dupes


GITHUB_API_URL = 'https://api.github.com'

def _create_private_repo(name, description, private=True):
    """Create a private repo"""

    url = '{}/orgs/{}/repos?access_token={}'.format(GITHUB_API_URL,
                                                    os.environ.get('ORG'), 
                                                    get_access_token())
    
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
            return

        # Send new repo data to create repo func
        _create_private_repo(self.request.get('repo-name'), 
                             self.request.get('repo-desc'))

        # Reload app
        self.redirect('/app')


class GetRepoData(BaseHandler):
    """List teams with access to the repo"""

    def post(self):
        
        # If data didn't come through, bail
        if not self.request.get('repo'):
            return

        # Get all teams in org
        all_teams = get_all_teams()
        
        # Get all teams with access to repo
        repo_teams = get_repo_teams(self.request.get('repo'))

        # Remove all dupes from list 
        data = remove_dupes(all_teams, repo_teams)

        # Send data back to app 
        self.response.out.write(data)


config = config()

app = webapp2.WSGIApplication([
    ('/create-repo', CreateRepo),
    ('/get-data', GetRepoData),
], config=config, debug=True)
