"""
Route users to the correct destination depending on their login status

This module detects whether the app is activated, and whether a user is logged
in, and consequently triggers the app activation process and user auth process 
respectively. 

"""

class DetectAppActivation(BaseHandler):
    """
    Detect if the app is activated and route the user accordingly. If the app
    is activated, detect if the user is logged in. If not, send to auth. 
    """

    def get(self):
        pass


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': ''  # get secret key
}

application = webapp2.WSGIApplication([
    ('/', DetectAppActivation),
], config=config, debug=True)
