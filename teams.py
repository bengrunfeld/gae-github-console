"""
All actions concerning teams
"""

import os
import webapp2
import json

from google.appengine.api import urlfetch

from auth import fetch_url
from auth import get_access_token
from basehandler import BaseHandler
from config import config


GITHUB_API_URL = 'https://api.github.com'


def get_all_teams():
    """Get all teams belonging to org"""
    
    # Create url 
    url = '{}/orgs/{}/teams?access_token={}'.format(GITHUB_API_URL,
                                                    os.environ.get('ORG'),
                                                    get_access_token())    
    # Fetch results from Github
    content = json.loads(fetch_url(url))

    # Create a dict to store results
    response = {} 

    for value in content:
        response[value.get('name')] = (value.get('id'), 
                                       value.get('permission'))

    return response


def get_repo_teams(repo):
    """Get all teams with access to repo"""

    # Create url
    url = '{}/repos/{}/{}/teams?access_token={}'.format(GITHUB_API_URL,
                                                       os.environ.get('ORG'),
                                                       repo,
                                                       get_access_token())

    # Fetch results from Github
    content = json.loads(fetch_url(url))
    
    # Create a dict to store results
    response = {} 

    for value in content:
        response[value.get('name')] = (value.get('id'), 
                                       value.get('permission'))

    
    return response


def remove_dupes(all_teams, repo_teams):
    """Remove duplicates from either list"""

    # Remove Owners from teasm
    del all_teams['Owners']

    # Make a copy of all_teams, since teams will be modified
    teams = dict(all_teams)

    # Remove dupes from all_teams
    for repo_team in repo_teams:
        if repo_team in teams:
            del teams[repo_team]
    
    # Send back all_teams as well, for add/remove team member functionality
    data = dict([
                ('teams', teams),
                ('all_teams', all_teams),
                ('team_collaborators', repo_teams)
                ])
                

    return json.dumps(data)

def add_team(team_id, repo):
    """Add team access to a repo"""

    # Build url for HTTP request
    url = '{}/teams/{}/repos/{}/{}?access_token={}'.format(
                                                GITHUB_API_URL,
                                                team_id,
                                                os.environ.get('ORG'),
                                                repo,
                                                get_access_token())
                                                
    # Give repo access to team
    fetch_url(url, urlfetch.PUT)


def remove_team(team_id, repo):
    """Remove team access from a repo"""

    # Build url for HTTP request
    url = '{}/teams/{}/repos/{}/{}?access_token={}'.format(
                                            GITHUB_API_URL,
                                            team_id,
                                            os.environ.get('ORG'),
                                            repo,
                                            get_access_token())

    # Remove repo access from a team
    fetch_url(url, urlfetch.DELETE)


def edit_team(team_name, team_id, edit_type):
    """Edit the access of a team"""

    url = '{}/teams/{}?access_token={}'.format(GITHUB_API_URL,
                                               team_id,
                                               get_access_token())

    # Get the required info to perform the query
    fields = {
        "name": team_name,
        "id": team_id,
        "permission": edit_type,
    }

    fetch_url(url, urlfetch.PATCH, json.dumps(fields))
          

def get_team_members(team_id):
    """Get the members of a given team"""

    # Get members belonging to the selected team 
    url = '{}/teams/{}/members?access_token={}'.format(
                                            GITHUB_API_URL,
                                            team_id,
                                            get_access_token())

    team_members = json.loads(fetch_url(url))

    return team_members


def get_all_org_members():
    """Get all members belonging to org"""

    url = '{}/orgs/{}/members?access_token={}'.format(GITHUB_API_URL,
                                                      os.environ.get('ORG'),
                                                      get_access_token())

    result = json.loads(fetch_url(url))


class AddTeam(BaseHandler):
    """Give repo access to a team"""

    def post(self):
        
        # If user isn't logged in, send to auth
        if not self.session.get('logged_in'):
            self.redirect('/auth')
            return

        # Add team
        add_team(self.request.get('team_id'), self.request.get('repo'))
 

class RemoveTeam(BaseHandler):
    """Remove repo access from a team"""

    def post(self):
        
        # If user isn't logged in, send to auth
        if not self.session.get('logged_in'):
            self.redirect('/auth')
            return

        # Remove team
        remove_team(self.request.get('team_id'), self.request.get('repo')) 


class EditTeam(BaseHandler):
    """Change the access of a team to a repo"""

    def post(self):
        
        # If user isn't logged in, send to auth
        if not self.session.get('logged_in'):
            self.redirect('/auth')
            return
       
        edit_team(
                self.request.get('team_name'), 
                self.request.get('team_id'),
                self.request.get('edit_type')
        ) 


class ChangeTeam(BaseHandler):
    """
    Print all the members of a team when a user chooses a different team to
    edit in the Team Members tab
    """

    def post(self):
        
        # If user isn't logged in, send to auth
        if not self.session.get('logged_in'):
            self.redirect('/auth')
            return

        # Get members for a given team
        team_members = get_team_members(self.request.get('team_id'))

        
        # Get all members belonging to org
        # all_members = get_all_org_members()

        # Remove dupes
        # members = remove_dupes(all_members, team_members)

        # response = {'team_members': team_members, 'all_members': all_members}
        # members = json.dumps(response)
        
        # Send members lists back to app
        self.response.out.write(team_members)
        

config = config()

app = webapp2.WSGIApplication([
    ('/add-team', AddTeam),
    ('/remove-team', RemoveTeam),
    ('/edit-team', EditTeam),
    ('/change-team', ChangeTeam),
], config=config, debug=True)

