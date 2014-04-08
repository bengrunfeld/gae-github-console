"""
Contains classes and functions that trigger the API actions in GhRequests

"""

import os
import sys
import datetime

LIB_PATH = os.path.join(os.getcwd(), 'lib')
if LIB_PATH not in sys.path:
    sys.path.insert(0, LIB_PATH)

import json
import jinja2
import webapp2

from basehandler import BaseHandler
from model import Log

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
            context = {"repos": repos, "username": self.session.get('login')}

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
        
        super(AccessDenied, self).log('Access was denied to user')

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

        if super(CreateRepo, self).query(url, 'POST', fields):

            # Construct the log message
            message = self.session.get('login')
            message += ' created a private repo named: '
            message += self.request.get('repo-name')
     
            super(CreateRepo, self).log(message)

            # Add default teams here. Replicate the code for multiple teams
            url = '/add-team'
            fields = {
                "repo": self.request.get('repo-name'),
                # "team_id": place team id here
            } 

            super(CreateRepo, self).query(url, 'POST', fields)

        self.redirect('/')
        return


class GetData(BaseHandler):
    """
    Get team and user data about a particular private repository
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
                    ('teams', teams),
                    ('all_teams', all_teams),
                    ('team_collaborators', team_collaborators)
                    ])
        response = json.dumps(resp)
        self.response.out.write(response)


class AddTeam(BaseHandler):
    """
    Add a team belonging to the organization to a private repository
    """

    def post(self):
        if (self.request.get('repo') and self.request.get('team_id')):

            # Get the required info to perform the query
            repo = self.request.get('repo')
            team_id = self.request.get('team_id')

            # Set the url
            url = '/teams/' + team_id + '/repos/' + ORG + '/' + repo

            # Send the request
            if super(AddTeam, self).query(url, 'PUT'):

                # Construct the log message
                message = self.session.get('login')
                message += ' added team: '
                message += self.request.get('team_name')
                message += ' to repo: '
                message += self.request.get('repo')
         
                super(AddTeam, self).log(message)


class RemoveTeam(BaseHandler):
    """
    Remove a team belonging to the organization from a private repository
    """

    def post(self):
        if (self.request.get('repo') and self.request.get('team_id')):

            # Get the required info to perform the query
            repo = self.request.get('repo')
            team_id = self.request.get('team_id')

            # Set the url
            url = '/teams/' + team_id + '/repos/' + ORG + '/' + repo

            # Remove the team from the repo 
            if super(RemoveTeam, self).query(url, 'DELETE'):
            
                # Construct the log message
                message = self.session.get('login')
                message += ' removed team: '
                message += self.request.get('team_name')
                message += ' from repo: '
                message += repo 
         
                super(RemoveTeam, self).log(message)

            return


class EditTeam(BaseHandler):
    """
    Edit the access level of a team. This will affect the access of a team to
    all repositories, not just a single repository.
    """

    def post(self):
        if (self.request.get('team_id') and self.request.get('edit_type')
                and self.request.get('team_name')):

            # Get the required info to perform the query
            fields = {
                        "name": self.request.get('team_name'),
                        "id": self.request.get('team_id'),
                        "permission": self.request.get('edit_type'),
                     }

            # Set the url
            url = '/teams/' + fields['id']

            # Edit the team's access 
            if super(EditTeam, self).query(url, 'PATCH', fields):

                # Construct the log message
                message = self.session.get('login')
                message += ' edited the access of team: '
                message += self.request.get('team_name')
                message += ' to have the access level of: '
                message += self.request.get('edit_type')
         
                super(EditTeam, self).log(message)

            return


class AddTeamMembers(BaseHandler):
    """
    Add members of the organization to a specific team
    """

    def post(self):
        # Check that necessary values exist
        if not self.request.get('users') and not self.request.get('team_id'):
            return

        # Get users and team id
        members = self.request.get('users')
        team_id = self.request.get('team_id')

        # Parse the list of members from JSON into a useable format
        users = json.loads(members)

        # Loop through the list of users and submit an add request for each
        for user in users:

            # Get the necessary info to make the request
            url = '/teams/' + team_id + '/members/' + user

            # Add member to team 
            if super(AddTeamMembers, self).query(url, 'PUT'):
                
                # Construct the log message
                message = self.session.get('login')
                message += ' added team member: '
                message += user 
                message += ' to team: '
                message += self.request.get('team_id')
         
                super(AddTeamMembers, self).log(message)

        return


class ChangeTeam(BaseHandler):
    """
    Print all the members of a team when a user chooses a different team to 
    edit in the Team Members tab
    """

    def post(self):

        # check that the necessary values exist
        if not self.request.get('team_id'):
            return

        # Get the info needed for the request
        url = '/teams/' + self.request.get('team_id') + '/members'

        # Send off the request and sort the results
        results = super(ChangeTeam, self).query(url)
        team_members = super(ChangeTeam, self).sort_results(results, 'single',
                                                    'login')

        # Get all members in the Org
        url = '/orgs/' + ORG + '/members'

        # Send off the request and sort the results
        results = super(ChangeTeam, self).query(url)
        all_members = super(ChangeTeam, self).sort_results(results, 'single',
                                                    'login')

        # Craft the response into a JSON object and send it back
        response = {'team_members': team_members, 'all_members': all_members}
        members = json.dumps(response)
        self.response.out.write(members)

        return


class RemoveTeamMember(BaseHandler):
    """
    Remove a team member from a team
    """

    def post(self):

        # Check that the necessary values exist
        if not self.request.get('team_id') and not self.request.get('user'):
            return

        # DELETE /teams/:id/members/:user
        url = ('/teams/' + self.request.get('team_id') + '/members/' +
                self.request.get('user'))

        # Remove a team member from the team 
        if super(RemoveTeamMember, self).query(url, 'DELETE'):

            # Construct the log message
            message = self.session.get('login')
            message += ' removed team member: '
            message += user 
            message += ' from team: '
            message += self.request.get('team_id')

            super(AddTeamMembers, self).log(message)

        return

class DisplayLogs(BaseHandler):
    """
    Display a set number of the most recent logs
    """

    def post(self):

        # Construct a from-date and a to-date
        from_datetime = self.request.get('from_date')
        to_datetime = self.request.get('to_date')

        # Example of correct formatting of datetime
        # from_value = datetime.datetime(2014, 4, 8, 18, 17, 29)
        # to_value = datetime.datetime(2014, 4, 8, 18, 17, 34)


        # If a datetime filter exists, query ndb for that
        if from_datetime and to_datetime:
            qry = Log.query(Log.datetime > from_datetime, 
                            Log.datetime < to_datetime).order(-Log.datetime)
        else:
            # No datetime filter exists, perform regular 
            qry = Log.query().order(-Log.datetime)

        # Now go and fetch the results
        results = qry.fetch(int(self.request.get('number_of_posts')))

        # Create a dictionary to store the response
        response = []

        # Perform a custom sort that concatenates content to datetime
        for result in results:
            if result.datetime and result.content:
                response.append(str(result.datetime) + ' ' + result.content) 

        # Dump the response out as JSON
        response = json.dumps(response)

        # Send the result of the query back to the AJAX calling it
        self.response.out.write(response)

        return


class Logout(BaseHandler):
    """
    Log a user out from their session
    """

    def get(self):

        # Log the user out of the app 
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
    ('/add-team', AddTeam),
    ('/remove-team', RemoveTeam),
    ('/edit-team', EditTeam),
    ('/logout', Logout),
    ('/display_token.*', DisplayToken),
    ('/change-team', ChangeTeam),
    ('/add-team-members', AddTeamMembers),
    ('/remove-team-member', RemoveTeamMember),
    ('/display-logs', DisplayLogs),
], config=config, debug=True)
