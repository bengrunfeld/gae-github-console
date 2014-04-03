"""
Contains classes and functions that trigger the API actions in GhRequests

"""

import os
import sys

LIB_PATH = os.path.join(os.getcwd(), 'lib')
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)

import json
import jinja2
import webapp2

from basehandler import BaseHandler
from ghrequests import GhRequests

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
ORG = os.environ.get('ORG')

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class MainClass(BaseHandler):
    """
    If no environment variable exists with the access token in it,
    auth the user as an admin. If it does exist, auth them as a regular
    user and let them use the app.
    """

    def get(self):

        # Admin hasn't auth'd via Github yet
        if not ACCESS_TOKEN and 'code' not in self.request.url:
            self.redirect('/get-auth-token')
            return

        # Admin has successfully auth'd via Github, now get Access Token
        if not ACCESS_TOKEN and 'code' in self.request.url:
            self.redirect('/get-access-token')
            return

        # Product activated, but User needs to auth via Github
        if (ACCESS_TOKEN and not 'code' in self.request.url and
                not self.session.get('github_member')):
            self.redirect('/get-auth-token')
            return

        # User has auth'd via Github, now get access token for them
        if ACCESS_TOKEN and 'code' in self.request.url:
            self.redirect('/get-access-token')
            return

        # User is auth'd and member of organization, send them to product
        if self.session.get('github_member'):
            # Get the private repos of the Org
            url = '/orgs/' + ORG + '/repos'
            results = super(MainClass, self).query(url)
            repos = super(MainClass, self).sort_results(results, 'multiple',
                                                        'name', 'private')
            page = 'index'
            context = {"repos": repos}

            super(MainClass, self).render(page, context)


class DisplayToken(BaseHandler):
    """
    Display the access token to an authorized owner of the organization
    """

    def get(self):
        # Template Settings
        page = 'login'
        context = {"access_token": self.request.get('access_token')}

        super(DisplayToken, self).render(page, context)


class AccessDenied(BaseHandler):
    """
    User is not a member of the organization. Deny access
    """

    def get(self):
        # Template Settings
        page = '403.html'
        context = ''

        super(AccessDenied, self).render(page, context)


class CreateRepo(BaseHandler):
    """
    Create a private repository
    """

    def post(self):
        fields = {
            "name": self.request.get('repo-name'),
            "description": self.request.get('repo-desc'),
            "private": True,
        }

        url = '/orgs/' + ORG + '/repos'
        super(CreateRepo, self).query(url, fields, 'POST')
        self.redirect('/')


class GetData(BaseHandler):
    """
    Get team and user data about a particular repository
    """

    def post(self):
        # No repo name exists, return to calling function 
        if not self.request.get('repo'):
            return

        if self.request.get('repo'):

            # Get the name of the repo that we want info on
            repo = self.request.get('repo')

            # Get all teams in the Org
            url = '/orgs/' + ORG + '/teams'
            results = super(GetData, self).query(url)
            teams = super(GetData, self).sort_results(results, 'teams')
 
            # Get all teams with access to the repo
            url = '/repos/' + ORG + '/' + repo + '/teams'
            results = super(GetData, self).query(url)
            team_collaborators = super(GetData, self).sort_results(results,
                                                                    'teams')

            # Get all members in the Org
            url = '/orgs/' + ORG + '/members'
            results = super(GetData, self).query(url)
            members = super(GetData, self).sort_results(results, 'single', 
                                                        'login')
            
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
    ('/display_token.*', DisplayToken),
], config=config, debug=True)
