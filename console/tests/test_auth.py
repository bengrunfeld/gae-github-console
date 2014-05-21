"""
Test all classes and functions in auth.py
""" 

import unittest

from google.appengine.api import urlfetch_service_pb

from google.appengine.ext import testbed


class BaseTestUrlFetch(unittest.TestCase):
    """Base class for any class using URL Fetch"""

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_urlfetch_stub()

    def tearDown(self):
        self.testbed.deactivate()


class TestUrlFetch(BaseTestUrlFetch):
    """Test if fetch_url sending legitimate requests"""

    def test_fetch_url(self):
        from console.auth import fetch_url

        # Grab content via a URL fetch
        content = fetch_url('https://google.com')

        # Test that content is not empty
        self.assertIsNotNone(content)


class TestGetUserName(unittest.TestCase):
    """Test that a valid username is being returned"""

    def test_get_username(self):
        from console.auth import get_user_name

        # Request username from GitHub 
        content = get_user_name()

        # Print content
        print(content)

        # Test that response does not equal error
        assertIsNotNone(content)
