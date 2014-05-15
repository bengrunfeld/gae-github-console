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
from logs import create_log


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


def remove_dupes(all_vals, select_vals):
    """Remove duplicates from either list"""

    # Remove dupes from all_teams
    for select_val in select_vals:
        if select_val in all_vals:
            del all_vals[select_val]

    return all_vals


def _get_team_name(team_id):
    """Get the name of a certain team"""

    # Create URL to get team name
    url = '{}/teams/{}?access_token={}'.format(GITHUB_API_URL,
                                               team_id,
                                               get_access_token())

    # Retrieve team name from result
    result = json.loads(fetch_url(url))

    return result['name']


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

    # Create a log entry
    message = '{} was added to the {} repo'.format(_get_team_name(team_id),
                                                   repo)
    create_log(message)


def _append_to_response(entities):
    """Append values to a list"""

    response = []

    for entity in entities:
        response.append(entity.get('login'))

    return response


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

    # Create a log entry
    message = '{} was removed from the {} repo'.format(_get_team_name(team_id),
                                                       repo)
    create_log(message)


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

    # Create a log entry
    message = '{} was given {} access'.format(team_name, edit_type)

    create_log(message)


def get_team_members(team_id):
    """Get the members of a given team"""

    # Get members belonging to the selected team
    url = '{}/teams/{}/members?access_token={}'.format(
          GITHUB_API_URL,
          team_id,
          get_access_token())

    team_members = json.loads(fetch_url(url))

    response = _append_to_response(team_members)

    return response


def get_all_org_members():

    """Get all members belonging to org"""

    url = '{}/orgs/{}/members?access_token={}'.format(GITHUB_API_URL,
                                                      os.environ.get('ORG'),
                                                      get_access_token())

    all_members = json.loads(fetch_url(url))

    response = _append_to_response(all_members)

    return response


def _add_members_to_team(team_id, members):
    """Add members of org to a team"""

    for member in members:
        url = '{}/teams/{}/members/{}?access_token={}'.format(
              GITHUB_API_URL,
              team_id,
              member,
              get_access_token())

        fetch_url(url, urlfetch.PUT)

    # Create a log entry
    message = '{} was added to {}'.format(members, _get_team_name(team_id))

    create_log(message)


def _remove_member_from_team(team_id, member):
    """Remove an org member from a team"""

    url = '{}/teams/{}/members/{}?access_token={}'.format(
          GITHUB_API_URL,
          team_id,
          member,
          get_access_token())

    fetch_url(url, urlfetch.DELETE)

    # Create a log entry
    message = '{} was removed from {}'.format(member, _get_team_name(team_id))

    create_log(message)


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
        remove_team(self.request.get('team_id'),
                    self.request.get('repo'))


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
        all_members = get_all_org_members()

        # Remove dupes
        all_members = list(set(all_members) - set(team_members))

        response = {
            'team_members': team_members,
            'all_members': all_members
        }

        members = json.dumps(response)

        # Send members lists back to app
        self.response.out.write(members)


class AddTeamMembers(BaseHandler):
    """Add a member of the org to the team"""

    def post(self):

        if not self.session.get('logged_in'):
            self.redirect('/auth')
            return

        # Add members to team
        _add_members_to_team(self.request.get('team_id'),
                             json.loads(self.request.get('users')))

        return


class RemoveTeamMember(BaseHandler):
    """Remove a member fo the org from a team"""

    def post(self):

        # Remove member from team
        _remove_member_from_team(self.request.get('team_id'),
                                 self.request.get('user'))
