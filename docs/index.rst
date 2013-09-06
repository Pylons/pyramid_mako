============
pyramid_mako
============

Overview
========

:term:`pyramid_mako` is a set of bindings that make templates written for the
:term:`Mako` templating system work under the :term:`Pyramid` web framework.

Installation
============

Install using setuptools, e.g. (within a virtualenv)::

  $ $myvenv/bin/easy_install pyramid_mako

Setup
=====

There are two ways to make sure that ``pyramid_mako`` is active.  Both
are completely equivalent:

#) Use the ``includeme`` function via ``config.include``::

    config.include('pyramid_mako')

#) Put a reference to ``pyramid_mako`` within the ``pyramid.includes`` value
   in your ``ini`` file configuration::

    pyramid.includes = pyramid_mako

Once activated either of these says, the following happens:

#) Files with the ``.mako`` or ``.mak`` extension are considered to be
   :term:`Mako` templates.

#) The :func:`pyramid_mako.add_mako_search_path` directive is added to
   the :term:`configurator` instance.

To setup the mako search path either one of the following steps must be taken:

#) Add ``mako.directories`` to your ``.ini`` settings file using the pyramid
   asset spec::
  
     mako.directories = yourapp:templates

#) Or Alternatively by using the ``add_mako_search_path`` directive
   attached to your application's :term:`configurator` instance also using
   the pyramid asset spec::

     config.add_mako_search_path("yourapp:templates")

.. warning::

    If you do not explicitly configure your mako search path it will
    default to the root of your application.  If configured in this way all
    subsequent paths will need to be specified relative to the root of your
    application's package.  For example:

    Without the search path configured:

    .. code-block:: text

        @view_config(renderer='templates/mytemplate.mako')
  
    With the search path configured:
      
    .. code-block:: text 
   
       @view_config(renderer='mytemplate.mako')

Usage
=====

Once :term:`pyramid_mako` been activated ``.mako`` templates
can be loaded either by looking up names that would be found on
the :term:`Mako` search path or by looking up asset specifications.

Template Lookups
----------------

The default lookup mechanism for templates uses the :term:`Mako`
search path. (specified with ``mako.directories`` or by using the 
add_mako_search_path directive on the :term:`configurator` instance.)

Rendering :term:`Mako` templates with a view like this is typically
done as follows (where the ``templates`` directory is expected to
live in the search path):

.. code-block:: python
 :linenos:

 from pyramid.view import view_config
 
 @view_config(renderer='mytemplate.mako')
 def myview(request):
     return {'foo':1, 'bar':2}

Rendering templates outside of a view (and without a request) can be
done using the renderer api:

.. code-block:: python
 :linenos:

 from pyramid.renderers import render_to_response
 render_to_response('mytemplate.mako', {'foo':1, 'bar':2})

Asset Specification Lookups
---------------------------

Looking up templates via asset specification is a feature specific
to :term:`Pyramid`.  For further info please see `Understanding
Asset Specifications
<http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/assets.html#understanding-asset-specifications>`_.
Overriding templates in this style uses the standard
`pyramid asset overriding technique
<http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/assets.html#overriding-assets>`_.

Settings
========

Mako derives additional settings to configure its template renderer. Many
of these settings are optional and only need to be set if they should be
different from the default.  The below values can be present in the ``.ini``
file used to configure the Pyramid application (in the ``app`` section
representing your Pyramid app) or they can be passed directly within the
``settings`` argument passed to a Pyramid Configurator.

pyramid.reload_templates

  ``true`` or ``false`` representing whether Mako templates should be
  reloaded when they change on disk.  Useful for development to be ``true``.

mako.directories

  A list of directory names or a newline-delimited string with each line
  representing a directory name.  These locations are where Mako will
  search for templates.  Each can optionally be an absolute resource
  specification (e.g. ``package:subdirectory/``).

Unit Testing
============

When you are running unit tests, you will be required to use
``config.include('pyramid_mako')`` to add :term:`pyramid_mako` so that it's
renderers are added to the config and can be used.::

    from pyramid import testing
    from pyramid.response import Response
    from pyramid.renderers import render
    
    # The view we want to test
    def some_view(request):
        return Response(render('mypkg:templates/home.mako', {'var': 'testing'}))

    class TestViews(unittest.TestCase):
        def setUp(self):
            self.config = testing.setUp()
            self.config.include('pyramid_mako')

        def tearDown(self):
            testing.tearDown()

        def test_some_view(self):
            from pyramid.testing import DummyRequest
            request = DummyRequest()
            response = some_view(request)
            # templates/home.mako starts with the standard <html> tag for HTML5
            self.assertTrue('<html' in response.body)

API Documentation
=================

.. toctree::
   :maxdepth: 1

   api

Reporting Bugs / Development Versions
=====================================

Visit http://github.com/Pylons/pyramid_mako to download development or tagged
versions.

Visit http://github.com/Pylons/pyramid_mako/issues to report bugs.

Indices and tables
------------------

* :ref:`glossary`
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
   :hidden:

   glossary
