##############################################################################
#
# Copyright (c) 2014 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, "README.rst")).read()
    CHANGES = open(os.path.join(here, "CHANGES.txt")).read()
except:
    README = CHANGES = ""

tests_require = [
    "WebTest >= 1.3.1", # py3 compat
    ]

docs_extras = [
    "Sphinx >= 1.8.1",  # Unicode character support
    "docutils",
    "repoze.sphinx.autointerface",
    "pylons-sphinx-themes >= 1.0.8",  # Ethical Ads
]

testing_extras = tests_require + [
    "nose",
    "coverage",
    ]

requires = [
    "pyramid",
    "Mako>=1.1.0",  # py38
]

setup(name="pyramid_mako",
      version="1.1.0",
      description="Mako template bindings for the Pyramid web framework",
      long_description=README + "\n\n" + CHANGES,
      classifiers=[
        "Development Status :: 6 - Mature",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Framework :: Pyramid",
        "License :: Repoze Public License",
        ],
      keywords=["web", "wsgi", "pyramid"],
      author="Bert JW Regeer",
      author_email="pylons-discuss@googlegroups.com",
      url="https://github.com/Pylons/pyramid_mako",
      project_urls={
          "Documentation": "https://docs.pylonsproject.org/projects/pyramid_mako/en/latest/",
          "Changelog": "https://github.com/Pylons/pyramid_mako/blob/master/CHANGES.txt",
          "Issue Tracker": "https://github.com/Pylons/pyramid_mako/issues",
      },
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      extras_require = {
          "testing":testing_extras,
          "docs":docs_extras,
          },
      tests_require=tests_require,
      test_suite="pyramid_mako.tests",
      entry_points="""""",
      )
