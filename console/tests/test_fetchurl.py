import unittest

from google.appengine.ext import testbed


class TestUrlFetch(unittest.TestCase):
    """Test if fetch_url sending legitimate requests"""

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_urlfetch_stub()

    def test_fetch_url(self):
        from console.auth import fetch_url

        # Grab content via a URL fetch
        content = fetch_url('https://google.com')

        # Test that content is not empty
        self.assertIsNotNone(content)

    def tearDown(self):
        self.testbed.deactivate()


if __name__ == '__main__':
    unittest.main()
