##############################################################################
#
# Copyright (c) 2010 Agendaless Consulting and Contributors.
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
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

tests_require = [
    'WebTest >= 1.3.1', # py3 compat
    ]

docs_extras = [
    'Sphinx',
    'docutils',
    'repoze.sphinx.autointerface',
    ]

testing_extras = tests_require + [
    'nose',
    'nose-selecttests',
    'coverage',
    'virtualenv', # for scaffolding tests
    ]
requires = [
    'pyramid',
    'Mako>=0.3.6' # strict undefined
]

setup(name='pyramid_mako',
      version='0.2',
      description='Mako template bindings for the Pyramid web framework',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Framework :: Pylons",
        "License :: Repoze Public License",
        ],
      keywords='web wsgi pylons pyramid',
      author="Bert JW Regeer",
      author_email="pylons-discuss@googlegroups.com",
      url="https://github.com/Pylons/pyramid_mako",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      extras_require = {
          'testing':testing_extras,
          'docs':docs_extras,
          },
      tests_require=tests_require,
      test_suite="pyramid_mako.tests",
      entry_points="""""",
      )
