"""
Test all classes and functions in auth.py
"""

import unittest

from mock import patch

from console.auth import fetch_url


#3rd PARTY
#@patch('console.auth.urlfetch.fetch')
#class FetchUrlTestCase(unittest.TestCase):

    #def test_fetch_200(self, fetch):
        #"""Ensure a request with a 200 result returns the content from the
        #request.
        #"""
        #content = "my foo content"
        #url = "my url"

        #fetch.return_value.status_code = 200
        #fetch.return_value.content = content

        #result = fetch_url(url)

        #self.assertEqual(result, content)

        #fetch.assert_called_once_with(
            #url=url, method=1, payload="",
            #headers={'Access-Control-Allow-Origin': '*'})

    #def test_fetch_not_200_and_not_300(self, fetch):
        #"""Ensure a request with a non 200 result returns None."""
        #content = "my foo content"
        #url = "my url"

        #fetch.return_value.status_code = 201
        #fetch.return_value.content = content

        #result = fetch_url(url)

        #self.assertIsNone(result)

        #fetch.assert_called_once_with(
            #url=url, method=1, payload="",
            #headers={'Access-Control-Allow-Origin': '*'})

    #def test_fetch_300(self, fetch):
        #"""Ensure a request with a non 200 result returns None."""
        #content = "my foo content"
        #url = "my url"

        #fetch.return_value.status_code = 300
        #fetch.return_value.content = content

        #result = fetch_url(url)

        #self.assertEqual(result, content)

        #fetch.assert_called_once_with(
            #url=url, method=1, payload="",
            #headers={'Access-Control-Allow-Origin': '*'})



#class TestAuthFunctions(unittest.TestCase):
    #"""Test the global functions in auth.py"""

    ## Define the url and the response
    #url = 'https://google.com'
    #response = 'Test response'

    #def test_fetch_url(self):
        #"""Test the fetch_url function"""

        #from console.auth import fetch_url

        ## Mock the fetch_url function
        #mock_fetch_url = MagicMock(spec=fetch_url, return_value=self.response)

        ## Test the function
        #assert mock_fetch_url(self.url) == self.response

    #def test_get_user_name(self):
        #"""Test the get_user_name funciton in auth.py"""

        #from console.auth import get_user_name

        #mock_get_user_name = MagicMock(spec=get_user_name,
                                       #return_value=self.response)

        #assert mock_get_user_name() == self.response

    #def test_create_flow_object(self):
        #from console.auth import _create_flow_object

        #mock_create_flow = MagicMock(spec=_create_flow_object,
                                     #return_value=self.response)

        #assert mock_create_flow() == self.response

    #def test_get_auth_uri(self):
        #from console.auth import _get_auth_uri

        #mock_get_auth_uri = MagicMock(spec=_get_auth_uri,
                                      #return_value=self.response)

        #assert mock_get_auth_uri() == self.response

    #def test_retrieve_code(self):
        #from console.auth import _retrieve_code

        #mock_retrieve_code = MagicMock(spec=_retrieve_code,
                                       #return_value=self.response)

        #assert mock_retrieve_code() == self.response

    #def test_get_org_name(self):
        #from console.auth import _get_org_name

        #mock_get_org_name = MagicMock(spec=_get_org_name,
                                      #return_value=self.response)

        #assert mock_get_org_name() == self.response

    #def test_user_is_org_member(self):
        #from console.auth import _user_is_org_member

        #test_user_is_org_member = MagicMock(spec=_user_is_org_member,
                                            #return_value=self.response)

        #assert test_user_is_org_member() == self.response

    #def test_user_is_org_admin(self):
        #from console.auth import _user_is_org_admin

        #mock_user_is_org_admin = MagicMock(spec=_user_is_org_admin,
                                            #return_value=self.response)

        #assert mock_user_is_org_admin() == self.response

    #def test_check_app_config(self):
        #from console.auth import _check_app_config

        #mock_check_app_config = MagicMock(spec=_check_app_config,
                                          #return_value=self.response)

        #assert mock_check_app_config() == self.response


#class TestAuthStorageFunctions(unittest.TestCase):
    #"""Test the functions in auth that use Storage"""

    #def test_get_access_token(self):
        #pass

    #def test_delete_access_token(self):
        #pass

## TODO: Figure out how to test classes, then write tests for Auth classes
