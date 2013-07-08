import os
import sys
import platform

from setuptools import setup, find_packages

setup(
    name='abl.pivotal_client',
    version='1.1.0',
    description='A simple client for Pivotal Tracker',
    author='Ableton Web Team',
    author_email='webteam@ableton.com',
    url='http://ableton.com/',
    zip_safe=False,
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        "console_scripts": [],
        },
    )
