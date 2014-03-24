"""
Functions that the main class calls

get_user
get_private_repos
get_organization_members
get_organization_teams
get_repo_collaborators
get_repo_teams
add_collaborator_to_repo
add_team
remove_team
edit_team
"""

import os
import json
import jinja2

from google.appengine.api import urlfetch
from basehandler import BaseHandler


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class GhRequests(BaseHandler):

    def get_user(self):
        access_token = os.environ.get('ACCESS_TOKEN')
        url = 'https://api.github.com/user?access_token=' + str(access_token)
        result = urlfetch.fetch(
            url=url,
            method=urlfetch.GET,
        )

        result = json.loads(result.content)

        if 'login' in result and result['login']:
            result = result['login']

        self.session['username'] = result

        return result

    def get_private_repos(self):
        # Get private repos that belong to the organization
        access_token = os.environ.get('ACCESS_TOKEN')

        url = 'https://api.github.com/orgs/' + os.environ.get('ORG') + \
            '/repos?access_token=' + str(access_token)

        results = urlfetch.fetch(
            url=url,
            method=urlfetch.GET,
        )

        results = json.loads(results.content)
        repos = []

        for result in results:
            if 'name' in result and result['name']  \
                    and 'private' in result and result['private']:

                repos.append(result['name'])

        return repos

    def get_organization_members(self):
        # Get members that belong to the organization
        access_token = os.environ.get('ACCESS_TOKEN')

        url = 'https://api.github.com/orgs/' + os.environ.get('ORG') \
            + '/members?access_token=' + str(access_token)

        results = urlfetch.fetch(
            url=url,
            method=urlfetch.GET,
        )

        results = json.loads(results.content)
        members = []

        for result in results:
            if 'login' in result and result['login']:
                members.append(result['login'])

        return members

    def get_organization_teams(self):
        # Get all the teams that belong to an organization

        access_token = os.environ.get('ACCESS_TOKEN')

        url = 'https://api.github.com/orgs/' + os.environ.get('ORG') \
            + '/teams?access_token=' + str(access_token)

        results = urlfetch.fetch(
            url=url,
            method=urlfetch.GET,
        )

        results = json.loads(results.content)
        teams = {}

        for result in results:
            if 'name' in result and result['name']:
                teams[result['name']] = (result['id'], result['permission'])

        return teams

    def get_repo_collaborators(self, repo):
        # Get members that belong to the organization
        access_token = os.environ.get('ACCESS_TOKEN')

        url = 'https://api.github.com/repos/' + os.environ.get('ORG') + '/' \
            + repo + '/contributors?access_token=' + str(access_token)

        results = urlfetch.fetch(
            url=url,
            method=urlfetch.GET,
        )
        if results.content:
            results = json.loads(results.content)
            collaborators = []

            for result in results:
                if 'login' in result and result['login']:
                    collaborators.append(result['login'])
        else:
            collaborators = []
        return collaborators

    def get_repo_teams(self, repo):
        # Get teams with access to a repo
        access_token = os.environ.get('ACCESS_TOKEN')

        # Get teams with access to a repo
        url = 'https://api.github.com/repos/' + os.environ.get('ORG') + '/' \
            + repo + '/teams?access_token=' + str(access_token)

        results = urlfetch.fetch(
            url=url,
            method=urlfetch.GET,
        )

        results = json.loads(results.content)
        repo_teams = {}

        for result in results:
            if 'name' in result and result['name']:
                repo_teams[
                    result['name']] = (
                    result['id'],
                    result['permission'],
                    )

        return repo_teams

    def add_collaborator_to_repo(self, collaborator, repo):
        # Add a member of the organization as a collaborator to a repository
        # PUT /repos/:owner/:repo/collaborators/:user
        access_token = os.environ.get('ACCESS_TOKEN')

        # Add collaborator to repo
        url = 'https://api.github.com/repos/' + os.environ.get('ORG') + '/' \
            + repo + '/collaborators/' + collaborator + '?access_token=' \
            + str(access_token)

        results = urlfetch.fetch(
            url=url,
            method=urlfetch.PUT,
        )

        results = json.loads(results.content)

    def add_team(self, repo, team_id):
        access_token = os.environ.get('ACCESS_TOKEN')

        url = 'https://api.github.com/teams/' + team_id + '/repos/' \
            + os.environ.get('ORG') + '/' + repo + '?access_token=' \
            + str(access_token)

        urlfetch.fetch(
            url=url,
            method=urlfetch.PUT,
        )

        return True

    def remove_team(self, repo, team_id):
        access_token = os.environ.get('ACCESS_TOKEN')

        url = 'https://api.github.com/teams/' + team_id + '/repos/' \
            + os.environ.get('ORG') + '/' + repo + '?access_token=' \
            + str(access_token)

        urlfetch.fetch(
            url=url,
            method=urlfetch.DELETE,
        )
        return True

    def edit_team(self, team_name, team_id, edit_type):
        access_token = os.environ.get('ACCESS_TOKEN')

        url = 'https://api.github.com/teams/' + team_id + '?access_token=' \
            + str(access_token)

        form_data = {
            "name": team_name,
            "id": team_id,
            "permission": edit_type,
        }

        data = json.dumps(form_data)
        urlfetch.fetch(
            url=url,
            payload=data,
            method=urlfetch.PATCH,
        )

        return True
