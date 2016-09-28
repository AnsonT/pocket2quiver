from distutils.core import setup
from setuptools import find_packages

print(find_packages(exclude=['docs', 'tests*']))

setup(
    # Application name:
    name="Pocket2Quiver",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Anson Tsao",
    author_email="tsaoa@acm.org",

    # Packages
    packages=find_packages(exclude=['docs', 'tests*']),

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://pypi.python.org/pypi/Pocket2Quiver_v010/",

    #
    license="LICENSE",
    description="Exports Pocket bookmarks to Quiver Notebook",

    long_description=open("README.md").read(),

    # Dependent packages (distributions)
    install_requires=[
      "docopt",
      "html2text",
      "peewee",
      "pocket-api",
      "prompt-toolkit",
      "py-dateutil",
      "PyYAML",
      "readability-lxml",
      "requests",
      "pathlib"
    ],

    entry_points = {
      'console_scripts': [
        'pocket2quiver=pocket2quiver.pocket2quiver:main'
      ]
    }
)
