import os
import sys


def setup_project():
    """This is the main entry point to setting up the app."""

    lib_path = os.path.join(os.getcwd(), 'lib')
    if lib_path not in sys.path:
        sys.path.insert(0, lib_path)

setup_project()

from console.main import app
