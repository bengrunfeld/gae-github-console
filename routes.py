"""
Route URLs to handlers.

This routes users to the correct handlers while passing along config based on
the URL.
"""

import webapp2

from console.config import config


def route_user():
    """Route user to correct handler"""

    return webapp2.WSGIApplication([
        webapp2.Route('/create-repo',
                      handler='console.repo.CreateRepo',
                      name='create_repo'),
        webapp2.Route('/get-data-repo',
                      handler='console.repo.GetRepoData',
                      name='get_repo_data'),
        webapp2.Route('/add-team',
                      handler='console.teams.AddTeam',
                      name='add_team'),
        webapp2.Route('/remove-team',
                      handler='console.teams.RemoveTeam',
                      name='remove_team'),
        webapp2.Route('/edit-team',
                      handler='console.teams.EditTeam',
                      name='edit_team'),
        webapp2.Route('/change-team',
                      handler='console.teams.ChangeTeam',
                      name='change_team'),
        webapp2.Route('/add-members-team',
                      handler='console.teams.AddTeamMembers',
                      name='add_team_members'),
        webapp2.Route('/remove-member-team',
                      handler='console.teams.RemoveTeamMember',
                      name='remove_team_members'),
        webapp2.Route('/display-logs',
                      handler='console.logs.DisplayLogs',
                      name='display_logs'),
        webapp2.Route('/email-logs',
                      handler='console.logs.EmailLogs',
                      name='email_logs'),
        webapp2.Route('/digest-logs',
                      handler='console.logs.LogDigest',
                      name='log_digest'),
        webapp2.Route('/auth',
                      handler='console.auth.AuthUser',
                      name='auth_user'),
        webapp2.Route('/code',
                      handler='console.auth.RetrieveToken',
                      name='retrieve_token'),
        webapp2.Route('/logout',
                      handler='console.auth.Logout',
                      name='logout'),
        webapp2.Route('/',
                      handler='console.main.RenderApp',
                      name='main_app'),
    ], config=config())
