============
pyramid_mako
============

Overview
========

:term:`pyramid_mako` is a set of bindings that makes templates written for the
:term:`Mako` templating system work under the :term:`Pyramid` web framework.
:term:`Mako` is a templating system written by Mike Bayer.

Installation
============

Install using setuptools, e.g. (within a virtualenv)::

  $ $VENV/bin/easy_install pyramid_mako

Setup
=====

There are two ways to make sure that ``pyramid_mako`` is active.  Both
are completely equivalent:

#) Use the ``includeme`` function via ``config.include``::

    config.include('pyramid_mako')

#) Put a reference to ``pyramid_mako`` within the ``pyramid.includes`` value
   in your ``ini`` file configuration::

    pyramid.includes = pyramid_mako

Once activated, files with the ``.mako`` or ``.mak`` extension are
considered to be :term:`Mako` templates.

Usage
=====

Once :term:`pyramid_mako` has been activated ``.mako`` templates can be
used by the Pyramid rendering system.

When used as the ``renderer`` argument of a view, the view must return a
``Response`` object or a Python ``dict``.  The ``Response`` object would
bypass the renderer entirely. Otherwise the items in the ``dict`` would be
available in the global template space. If the view callable returns anything
but a ``Response`` object or a ``dict``, an error will likely be raised.

.. _template_lookups:

Template Lookup Mechanisms
--------------------------

There are several ways for Pyramid to find your :term:`Mako` templates.

Asset Specifications
~~~~~~~~~~~~~~~~~~~~

Templates may always be defined using an :term:`asset specification`. These
are strings which define an absolute location of the template, relative to
some Python package. For example, ``myapp.views:templates/home.mako``.
These specifications are supported throughout Pyramid and provide a
fool-proof way to find any supporting assets bundled with your application.

Here's an example view configuration which uses an
:term:`asset specification`:

.. code-block:: python
   :linenos:

   @view_config(renderer='mypackage:templates/foo.mak')
   def hello_world(request):
       return {'a':'1'}

Asset specifications have some significant benefits in Pyramid, as they
are fully overridable. An addon package can ship with code looking to
render all of its rendering done using asset specs. Later another package
can include the addon and provide customized templates without having to
actually modify the addon package. See :ref:`overriding_assets_section` for
more information.

Caller-Relative Template Lookup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, templates are discovered relative to the caller's package. This
means that if you define a view in a Python module, the templates would
be found relative to the module's directory on the filesystem.

Let's look at an example:

.. code-block:: python
   :linenos:

   @view_config(renderer='templates/mytemplate.mako')
   def myview(request):
       return {'foo': 1, 'bar': 2}

Imagine that the above code is in a ``myapp.admin.views`` module. The template
would be relative to that module on the filesystem, as shown below::

   myapp
   |- __init__.py
   `- admin
      |- views.py
      `- templates
         `- mytemplate.mako

One significant advantage of this approach over search paths (described below)
is that the path is actually converted into an :term:`asset specification`
in the background. This allows the template lookup to be modified using
Pyramid's powerful asset overriding APIs such as ``config.override_asset``.

Caller-relative lookup also avoids naming collisions which can be common in a
search path-based approach.

Search Path-Based Template Lookup
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When used outside of Pyramid, Mako's default lookup mechanism is a search
path. To use this mechanism within Pyramid, simply define the
search path using the ``mako.directories`` configuration setting.

Rendering :term:`Mako` templates with a search path is typically done as
follows:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(renderer='mytemplate.mako')
   def myview(request):
       return {'foo':1, 'bar':2}

We are now dependent on our configuration settings to tell us where the
template may be located. Commonly a ``templates`` directory is created
at the base of the package and the configuration file will include
the following directive::

    mako.directories = mypkg:templates

Templates Including Templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mako allows template inheritance as well as other mechanisms for templates
to load each other. The lookup mechanisms supported in these cases include
asset specifications and template-relative names.

Automatically Reloading Templates
---------------------------------

It's often convenient to see changes you make to a template file appear
immediately without needing to restart the application process. Pyramid allows
you to configure your application development environment so that a change to a
template will be automatically detected, and the template will be reloaded on
the next rendering.

.. warning::

   Auto-template-reload behavior is not recommended for production sites as it
   slows rendering slightly; it's usually only desirable during development.

In order to turn on automatic reloading of templates, you can use a
configuration file setting, or an environment variable.

To use a setting in the application ``.ini`` file for the same
purpose, set the ``pyramid.reload_templates`` key to ``true`` within the
application's configuration section, e.g.:

.. code-block:: ini
   :linenos:

   [app:main]
   use = egg:MyProject
   pyramid.reload_templates = true

To use an environment variable, start your application under a shell
using the ``PYRAMID_RELOAD_TEMPLATES`` operating system environment
variable set to ``1``, For example:

.. code-block:: text

   $ PYRAMID_RELOAD_TEMPLATES=1 bin/pserve myproject.ini

A Sample Mako Template
----------------------

Here's what a simple :term:`Mako` template used under ``pyramid_mako`` might
look like:

.. code-block:: xml
   :linenos:

   <html>
   <head>
       <title>${project} Application</title>
   </head>
     <body>
        <h1 class="title">Welcome to <code>${project}</code>, an
	 application generated by the <a
	 href="http://docs.pylonsproject.org/projects/pyramid/en/latest/"
        >pyramid</a> web framework.</h1>
     </body>
   </html>

This template doesn't use any advanced features of Mako, only the
``${}`` replacement syntax for names that are passed in as
:term:`renderer globals`. See the `the Mako documentation
<http://www.makotemplates.org/>`_ to use more advanced features.

Template Variables provided by Pyramid
--------------------------------------

:term:`Pyramid` by default will provide a set of variables that are available
within your templates, please see :ref:`renderer_system_values` for more
information about those variables.

.. note::

   There is one variable that has to be renamed due to having an naming conflict
   with an internal Mako variable.

   ``context`` will be renamed to ``_context``

   To output the name of the current context you would use the following:

   .. code-block:: mako

      <div>Context name: ${_context.__name__}</div>

Using A Mako def name Within a Renderer Name
--------------------------------------------

Sometimes you'd like to render a ``def`` inside of a Mako template instead of
the full Mako template. To render a def inside a Mako template, given a
:term:`Mako` template file named ``foo.mak`` and a def named ``bar``, you can
configure the template as a :term:`renderer` like so:

.. code-block:: python
   :linenos:

   from pyramid.view import view_config

   @view_config(renderer='foo#bar.mak')
   def my_view(request):
       return {'project':'my project'}

The above will render the ``bar`` def from within the ``foo.mak`` template
instead of the entire template.

.. _adding_or_overriding_renderers:

Adding or Overriding a Renderer
-------------------------------

By default, pyramid_mako registers two renderers, one for ``.mako`` and
another for ``.mak`` file extensions. The configuration for these renderers
are loaded from the ``mako.`` settings in your ini file.

It's possible to add Mako renderers for alternate file extensions, or
override the default ``.mak`` and ``.mako`` renderers with your own settings
using the :func:`pyramid_mako.add_mako_renderer` directive.

.. code-block:: python
   :linenos:

   config.include('pyramid_mako')
   config.add_mako_renderer('.mak', settings_prefix='mymak.')
   config.add_mako_renderer('.html')
   config.add_mako_renderer('.email', settings_prefix='makoemail.')

At the end of this setup, there will be 4 renderers registered. ``.mako`` and
``.html`` renderers are loaded from the ``mako.`` settings, and ``.mak`` is
using the ``mymak.`` settings. Finally ``.email`` templates will be using
the ``makoemail.`` settings. Some example usage follows:

.. code-block:: python
   :linenos:

   from pyramid.renderers import render

   @view_config(renderer='foo.html')
   def show_email(request):
       email_body = render('hello.email', {})
       return {
           'email_body': email_body,
       }

.. _mako_template_renderer_settings:

Settings
========

Mako derives additional settings to configure its template renderer. Many of
these settings are optional and only need to be set if they should be different
from the default.  The below values can be present in the ``.ini`` file used to
configure the Pyramid application (in the ``app`` section representing your
Pyramid app) or they can be passed directly within the ``settings`` argument
passed to a Pyramid Configurator.  The Mako Template Renderer uses a subclass
of Mako's `template lookup
<http://www.makotemplates.org/docs/usage.html#usage_lookup>`_ and accepts
several arguments to configure it.  These settings match those arguments.

Mako Directories
----------------

The value(s) supplied here are passed in as the template directories. They
should be in :term:`asset specification` format, for example:
``my.package:templates`` would specify the ``templates`` folder relative
to the location of the ``my.package`` Python package.

+-----------------------------+
| Config File Setting Name    |
+=============================+
|  ``mako.directories``       |
|                             |
|                             |
|                             |
+-----------------------------+

Mako Module Directory
---------------------

The value supplied here tells Mako where to store compiled Mako templates. If
omitted, compiled templates will be stored in memory. This value should be an
absolute path, for example: ``%(here)s/data/templates`` would use a directory
called ``data/templates`` in the same parent directory as the INI file. The
folder can also be an asset specification, defining a directory relative to
the package.

+-----------------------------+
| Config File Setting Name    |
+=============================+
|  ``mako.module_directory``  |
|                             |
|                             |
|                             |
+-----------------------------+

Mako Input Encoding
-------------------

The encoding that Mako templates are assumed to have. By default this is set
to ``utf-8``. If you wish to use a different template encoding, this value
should be changed accordingly.

+-----------------------------+
| Config File Setting Name    |
+=============================+
|  ``mako.input_encoding``    |
|                             |
|                             |
|                             |
+-----------------------------+

Mako Error Handler
------------------

A callable (or a :term:`dotted Python name` which names a callable) which is
called whenever Mako compile or runtime exceptions occur. The callable is
passed the current context as well as the exception. If the callable returns
True, the exception is considered to be handled, else it is re-raised after
the function completes. Is used to provide custom error-rendering functions.

+-----------------------------+
| Config File Setting Name    |
+=============================+
|  ``mako.error_handler``     |
|                             |
|                             |
|                             |
+-----------------------------+

Mako Default Filters
--------------------

List of string filter names that will be applied to all Mako expressions.

+-----------------------------+
| Config File Setting Name    |
+=============================+
|  ``mako.default_filters``   |
|                             |
|                             |
|                             |
+-----------------------------+

Mako Import
-----------

String list of Python statements, typically individual "import" lines, which
will be placed into the module level preamble of all generated Python modules.


+-----------------------------+
| Config File Setting Name    |
+=============================+
|  ``mako.imports``           |
|                             |
|                             |
|                             |
+-----------------------------+


Mako Strict Undefined
---------------------

``true`` or ``false``, representing the "strict undefined" behavior of Mako
(see `Mako Context Variables
<http://docs.makotemplates.org/en/latest/runtime.html#context-variables>`_).  By
default, this is ``false``.

+-----------------------------+
| Config File Setting Name    |
+=============================+
|  ``mako.strict_undefined``  |
|                             |
|                             |
|                             |
+-----------------------------+

Mako Preprocessor
-----------------

A callable (or a :term:`dotted Python name` which names a callable) which is
called to preprocess the source before the template is called.  The callable
will be passed the full template source before it is parsed. The return
result of the callable will be used as the template source code.


+-----------------------------+
| Config File Setting Name    |
+=============================+
|  ``mako.preprocessor``      |
|                             |
|                             |
|                             |
+-----------------------------+

Reloading Templates
-------------------

When this value is true, templates are automatically reloaded whenever they are
modified without restarting the application, so you can see changes to
templates take effect immediately during development.  This flag is meaningful
to most template rendering add-ons.

+---------------------------------+--------------------------------+
| Environment Variable Name       | Config File Setting Name       |
+=================================+================================+
| ``PYRAMID_RELOAD_TEMPLATES``    |  ``pyramid.reload_templates``  |
|                                 |                                |
|                                 |                                |
|                                 |                                |
+---------------------------------+--------------------------------+

Unit Testing
============

When you are running unit tests, you will be required to use
``config.include('pyramid_mako')`` to add :term:`pyramid_mako` so that its
renderers are added to the config and can be used.:

.. code-block:: python

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
