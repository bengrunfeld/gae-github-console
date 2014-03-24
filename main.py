"""
Contains classes and functions that trigger the API actions in GhRequests

"""

import os
import json
import jinja2
import webapp2

from google.appengine.api import urlfetch
from basehandler import BaseHandler
from githubauth import GithubAuth
from ghrequests import GhRequests


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainClass(GithubAuth, GhRequests):
    """
    If no environment variable exists with the access token in it,
    auth the user as an admin. If it does exist, auth them as a regular
    user.
    """

    def get(self):

        if os.environ.get('ACCESS_TOKEN'):
            # Set a user name
            if self.session.get('username'):
                username = self.session.get('username')
            else:
                username = 'User'

            # Auth the user
            if not self.session.get('access_token'):
                super(MainClass, self).auth_user()

            # Get private repos
            repos = super(MainClass, self).get_private_repos()

            # Template Settings
            context = {
                "username": username,
                "repos": repos,
                "org": os.environ.get('ORG'),
            }

            temp = 'templates/index.html'

            template = JINJA_ENVIRONMENT.get_template(temp)
            self.response.write(template.render(context))

        else:
            # Get an Access Token
            access_token = super(MainClass, self).auth_admin()

            # Template Settings
            context = {
                "username": "admin",
                "access_token": access_token,
            }
            temp = 'templates/login.html'

            template = JINJA_ENVIRONMENT.get_template(temp)
            self.response.write(template.render(context))


class AccessDenied(BaseHandler):
    """
    User is not a member of the organization. Deny access
    """

    def get(self):

        # For later
        # client.send('HTTP/1.0 403 Access Denied\r\n')

        # Template Settings
        temp = 'templates/403.html'
        context = ''

        template = JINJA_ENVIRONMENT.get_template(temp)
        self.response.write(template.render(context))


class CreateRepo(GhRequests):
    """
    Create a private repository
    """

    def post(self):
        access_token = os.environ.get('ACCESS_TOKEN')
        fields = {
            "name": self.request.get('repo-name'),
            "description": self.request.get('repo-desc'),
            "private": True,
        }
        url = 'https://api.github.com/orgs/' + os.environ.get('ORG') \
            + '/repos?access_token=' + str(access_token)
        data = json.dumps(fields)
        urlfetch.fetch(
            url=url,
            payload=data,
            method=urlfetch.POST,
        )

        self.redirect('/')


class GetData(GhRequests):
    """
    Get team and user data about a particular repository
    """

    def post(self):
        # Get collaborators for a specific repo
        if self.request.get('repo'):
            repo = self.request.get('repo')
            members = super(GetData, self).get_organization_members()
            teams = super(GetData, self).get_organization_teams()
            team_collaborators = super(GetData, self).get_repo_teams(repo)
        else:
            members = ''
            repo = ''
            teams = ''
            team_collaborators = ''

        # Make a copy of all teams, as teams will be altered
        all_teams = dict(teams)

        # Remove duplicates from teams
        if(team_collaborators):
            for team_collaborator in team_collaborators:
                if team_collaborator in teams:
                    del teams[team_collaborator]

        # Remove Owners from teams and all_teams as we do not want to provide
        # access to this
        del teams['Owners']
        del all_teams['Owners']

        # Build a JSON reponse
        resp = dict([
                    ('members', members),
                    ('teams', teams),
                    ('all_teams', all_teams),
                    ('team_collaborators', team_collaborators)
                    ])
        response = json.dumps(resp)
        self.response.out.write(response)


class AddCollaborator(GhRequests):
    """
    Add a collaborator to a repo
    """

    def post(self):

        if (self.request.get('repo') and self.request.get('collaborator')):
            repo = self.request.get('repo')
            collaborator = self.request.get('collaborator')
            super(
                AddCollaborator,
                self
                ).add_collaborator_to_repo(collaborator, repo)


class AddTeam(GhRequests):
    """
    Add repo access to a team
    """

    def post(self):
        if (self.request.get('repo') and self.request.get('team_id')):
            repo = self.request.get('repo')
            team_id = self.request.get('team_id')
            super(AddTeam, self).add_team(repo, team_id)


class RemoveTeam(GhRequests):
    """
    Remove repo access from a team
    """

    def post(self):
        if (self.request.get('repo') and self.request.get('team_id')):
            repo = self.request.get('repo')
            team_id = self.request.get('team_id')
            super(RemoveTeam, self).remove_team(repo, team_id)


class EditTeam(GhRequests):
    """
    Edit the access level of a team_collaborators
    """

    def post(self):
        if (self.request.get('team_id') and self.request.get('edit_type')
                and self.request.get('team_name')):
            team_id = self.request.get('team_id')
            team_name = self.request.get('team_name')
            edit_type = self.request.get('edit_type')
            if 'admin' in edit_type:
                return False
            else:
                super(EditTeam, self).edit_team(
                    team_name,
                    team_id,
                    edit_type,
                    )


class Logout(BaseHandler):
    """
    Log a user out from their session
    """

    def get(self):

        # Delete all session variables
        self.session.clear()

        # Redirect to Github logout
        self.redirect('https://github.com/logout')


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': os.environ.get('SESSION_SECRET'),
}

application = webapp2.WSGIApplication([
    ('/', MainClass),
    ('/403', AccessDenied),
    ('/create-repo', CreateRepo),
    ('/get-data', GetData),
    ('/add-collaborator', AddCollaborator),
    ('/add-team', AddTeam),
    ('/remove-team', RemoveTeam),
    ('/edit-team', EditTeam),
    ('/logout', Logout),
], config=config, debug=True)
