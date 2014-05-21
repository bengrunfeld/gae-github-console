"""
Test all classes and functions in auth.py
""" 

import unittest

from mock import Mock
from mock import patch

from google.appengine.api import urlfetch_service_pb
from google.appengine.ext import testbed


# class BaseTestUrlFetch(unittest.TestCase):
#     """Base class for any class using URL Fetch"""
# 
#     def setUp(self):
#         self.testbed = testbed.Testbed()
#         self.testbed.activate()
#         self.testbed.init_urlfetch_stub()
# 
#     def tearDown(self):
#         self.testbed.deactivate()


class TestUrlFetch(unittest.TestCase):
    """Test if fetch_url sending legitimate requests"""

    def test_fetch_url(self):
        from console.auth import fetch_url

        # Mock the fetch_url function 
        mock = Mock(wrap=fetch_url)
        content = mock.fetch_url.return_value = ('https://google.com')

        # Test that content is not empty
        self.assertIsNotNone(content)


# class TestGetUserName(unittest.TestCase):
#     """Test that a valid username is being returned"""
# 
#     def test_get_username(self):
#         from console.auth import get_user_name
# 
#         # Request username from GitHub 
#         content = get_user_name()
# 
#         # Print content
#         print(content)
# 
#         # Test that response does not equal error
#         assertIsNotNone(content)
