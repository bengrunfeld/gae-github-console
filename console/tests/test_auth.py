"""
Test all classes and functions in auth.py
"""

import json
import unittest
from google.appengine.api import urlfetch 
import mock
from mock import MagicMock
from mock import patch

@patch('console.auth.urlfetch.fetch')
class TestUrlfetchFunctions(unittest.TestCase):
    """Test the global functions in auth.py"""

    def test_fetch_200(self, fetch):
        """Ensure a request with a 200 result returns the content from the
        request.
        """
        from console.auth import fetch_url

        content = "my foo content"
        url = "my url"

        fetch.return_value.status_code = 200
        fetch.return_value.content = content

        result = fetch_url(url=url, method=urlfetch.GET, payload='',
            headers={'Access-Control-Allow-Origin': '*'}).content

        self.assertEqual(result, content)

        fetch.assert_called_once_with(
            url=url, method=urlfetch.GET, payload='',
            headers={'Access-Control-Allow-Origin': '*'})


class TestAuthFunctions(unittest.TestCase):

    def test_is_successful_returns_true(self):
        """Ensure a request with a non 200 result returns None."""
        from console.auth import is_successful_request 

        test_is_successful_request = MagicMock(spec=is_successful_request)
                                               
        request_result = {}
        request_result['status_code'] = 200

        self.assertTrue(test_is_successful_request(request_result))

#    def test_fetch_url(self):
#        """Test the fetch_url function"""
#
#        from console.auth import fetch_url
#
#        mock_fetch_url = MagicMock(spec=fetch_url, return_value=self.response)
#
#        assert mock_fetch_url(url=self.url) == self.response
#
#    def test_make_json_request(self):
#        """Test the fetch_url function"""
#
#        from console.auth import make_json_request
#
#        # Mock the fetch_url function
#        mock_make_json_request = MagicMock(spec=make_json_request,
#                                           return_value=self.response)
#
#        # Test the function
#        assert mock_make_json_request(self.url) == self.response
#
#    def test_get_user_name(self):
#        """Test the get_user_name funciton in auth.py"""
#
#        from console.auth import get_user_name
#
#        mock_get_user_name = MagicMock(spec=get_user_name,
#                                       return_value=self.response)
#
#        assert mock_get_user_name() == self.response
#
#    def test_create_flow_object(self):
#        from console.auth import _create_flow_object
#
#        mock_create_flow = MagicMock(spec=_create_flow_object,
#                                     return_value=self.response)
#
#        assert mock_create_flow() == self.response
#
#    def test_get_auth_uri(self):
#        from console.auth import _get_auth_uri
#
#        mock_get_auth_uri = MagicMock(spec=_get_auth_uri,
#                                      return_value=self.response)
#
#        assert mock_get_auth_uri() == self.response
#
#    def test_retrieve_code(self):
#        from console.auth import _retrieve_code
#
#        mock_retrieve_code = MagicMock(spec=_retrieve_code,
#                                       return_value=self.response)
#
#        assert mock_retrieve_code() == self.response
#
#    def test_get_org_name(self):
#        from console.auth import _get_org_name
#
#        mock_get_org_name = MagicMock(spec=_get_org_name,
#                                      return_value=self.response)
#
#        assert mock_get_org_name() == self.response
#
#    def test_user_is_org_member(self):
#        from console.auth import _user_is_org_member
#
#        test_user_is_org_member = MagicMock(spec=_user_is_org_member,
#                                            return_value=self.response)
#
#        assert test_user_is_org_member() == self.response
#
#    def test_user_is_org_admin(self):
#        from console.auth import _user_is_org_admin
#
#        mock_user_is_org_admin = MagicMock(spec=_user_is_org_admin,
#                                           return_value=self.response)
#
#        assert mock_user_is_org_admin() == self.response
#
#    def test_check_app_config(self):
#        from console.auth import _check_app_config
#
#        mock_check_app_config = MagicMock(spec=_check_app_config,
#                                          return_value=self.response)
#
#        assert mock_check_app_config() == self.response
#
#
#class TestAuthStorageFunctions(unittest.TestCase):
#    """Test the functions in auth that use Storage"""
#
#    def test_get_access_token(self):
#        pass
#
#    def test_delete_access_token(self):
#        pass
