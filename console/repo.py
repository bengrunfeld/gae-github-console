"""
Create a new private repo belonging to the organization
"""

import os
import json

from google.appengine.api import urlfetch

from auth import get_access_token
from auth import get_user_name
from auth import make_json_request
from basehandler import BaseHandler
from logs import create_log
from teams import add_team
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
    # fetch_url(url, urlfetch.POST, json.dumps(fields))
    make_json_request(url, method=urlfetch.POST, payload=json.dumps(fields))

    # Create a log entry
    message = '{} created the {} repo'.format(get_user_name(), name)
    create_log(message)


def _auto_add_teams_to_repo(repo, teams):
    """Automatically adds specified teams to newly created repositories"""

    for team in teams:
        add_team(team, repo)


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

        # Automatically add set teams to the new private repo
        teams = []  # Add team id's here

        _auto_add_teams_to_repo(self.request.get('repo-name'), teams)

        # Reload app
        self.redirect('/')


class GetRepoData(BaseHandler):
    """List teams with access to the repo"""

    def post(self):

        # If data didn't come through, bail
        if not self.request.get('repo'):
            return

        # Get all teams in org
        all_teams = get_all_teams()
        del all_teams['Owners']

        # Get all teams with access to repo
        repo_teams = get_repo_teams(self.request.get('repo'))

        # Make a copy of all_teams, since teams will be modified
        teams = dict(all_teams)

        # Remove all dupes from list
        teams = remove_dupes(teams, repo_teams)

        # Send back all_teams as well, for add/remove team member functionality
        data = dict([
            ('teams', teams),
            ('all_teams', all_teams),
            ('team_collaborators', repo_teams)
        ])

        # Send data back to app
        self.response.out.write(json.dumps(data))
