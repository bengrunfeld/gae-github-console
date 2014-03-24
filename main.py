"""
The main class that drives most of the program

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
    def get(self):

        # For later
        # client.send('HTTP/1.0 403 Access Denied\r\n')

        # Template Settings
        temp = 'templates/403.html'
        context = ''

        template = JINJA_ENVIRONMENT.get_template(temp)
        self.response.write(template.render(context))


class CreateRepo(GhRequests):

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

    def post(self):
        # Add a collaborator to the repo
        if (self.request.get('repo') and self.request.get('collaborator')):
            repo = self.request.get('repo')
            collaborator = self.request.get('collaborator')
            super(
                AddCollaborator,
                self
                ).add_collaborator_to_repo(collaborator, repo)
        else:
            print('nope')


class AddTeam(GhRequests):

    def post(self):
        if (self.request.get('repo') and self.request.get('team_id')):
            repo = self.request.get('repo')
            team_id = self.request.get('team_id')
            super(AddTeam, self).add_team(repo, team_id)


class RemoveTeam(GhRequests):

    def post(self):
        if (self.request.get('repo') and self.request.get('team_id')):
            repo = self.request.get('repo')
            team_id = self.request.get('team_id')
            super(RemoveTeam, self).remove_team(repo, team_id)


class EditTeam(GhRequests):

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
