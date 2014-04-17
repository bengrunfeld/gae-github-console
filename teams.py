"""
All actions concerning teams
"""

import os
import webapp2
import json

from auth import fetch_url
from auth import get_access_token


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
    teams = all_teams

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


