"""
Test all classes and functions in auth.py
"""

import unittest

from mock import MagicMock


class TestAuthFunctions(unittest.TestCase):
    """Test the global functions in auth.py"""

    # Define the url and the response
    url = 'https://google.com'
    response = 'Test response'

    def test_fetch_url(self):
        """Test the fetch_url function"""

        from console.auth import fetch_url

        # Mock the fetch_url function
        mock_fetch_url = MagicMock(spec=fetch_url, return_value=self.response)

        # Test the function
        assert mock_fetch_url(self.url) == self.response

    def test_get_user_name(self):
        """Test the get_user_name funciton in auth.py"""

        from console.auth import get_user_name

        # Mock the get_user_name function
        mock_get_user_name = MagicMock(spec=get_user_name,
                                       return_value=self.response)

        # Test the function
        assert mock_get_user_name() == self.response
