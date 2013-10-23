import os
import posixpath
import sys
import warnings

from zope.interface import (
    Interface,
    )

from pyramid.asset import (
    resolve_asset_spec,
    abspath_from_asset_spec,
    )

from pyramid.compat import (
    is_nonstr_iter,
    reraise,
    )

from pyramid.settings import asbool

from mako.lookup import TemplateLookup
from mako.exceptions import TopLevelLookupException
from mako.exceptions import text_error_template

class PkgResourceTemplateLookup(TemplateLookup):
    """TemplateLookup subclass that handles asset specification URIs"""
    def adjust_uri(self, uri, relativeto):
        """Called from within a Mako template, avoids adjusting the
        uri if it looks like an asset specification"""
        # Don't adjust asset spec names
        isabs = os.path.isabs(uri)
        if (not isabs) and (':' in uri):
            return uri
        if not(isabs) and ('$' in uri):
            return uri.replace('$', ':')
        if relativeto is not None:
            relativeto = relativeto.replace('$', ':')
            if not(':' in uri) and (':' in relativeto):
                if uri.startswith('/'):
                    return uri
                pkg, relto = relativeto.split(':')
                _uri = posixpath.join(posixpath.dirname(relto), uri)
                return '{0}:{1}'.format(pkg, _uri)
            if not(':' in uri) and not(':' in relativeto):
                return posixpath.join(posixpath.dirname(relativeto), uri)
        return TemplateLookup.adjust_uri(self, uri, relativeto)

    def get_template(self, uri):
        """Fetch a template from the cache, or check the filesystem
        for it

        In addition to the basic filesystem lookup, this subclass will
        use pkg_resource to load a file using the asset
        specification syntax.

        """
        isabs = os.path.isabs(uri)
        if (not isabs) and (':' in uri):
            # Windows can't cope with colons in filenames, so we replace the
            # colon with a dollar sign in the filename mako uses to actually
            # store the generated python code in the mako module_directory or
            # in the temporary location of mako's modules
            adjusted = uri.replace(':', '$')
            try:
                if self.filesystem_checks:
                    return self._check(adjusted, self._collection[adjusted])
                else:
                    return self._collection[adjusted]
            except KeyError:
                pname, path = resolve_asset_spec(uri)
                srcfile = abspath_from_asset_spec(path, pname)
                if os.path.isfile(srcfile):
                    return self._load(srcfile, adjusted)
                raise TopLevelLookupException(
                    "Can not locate template for uri %r" % uri)
        return TemplateLookup.get_template(self, uri)

class MakoRendererFactory(object):
    lookup = None

    def __call__(self, info):
        defname = None
        asset, ext = info.name.rsplit('.', 1)
        if '#' in asset:
            asset, defname = asset.rsplit('#', 1)

        path = '%s.%s' % (asset, ext)

        return MakoLookupTemplateRenderer(path, defname, self.lookup)

class MakoRenderingException(Exception):
    def __init__(self, text):
        self.text = text

    def __repr__(self):
        return self.text

    __str__ = __repr__

class MakoLookupTemplateRenderer(object):
    """ Render a :term:`Mako` template using the template
    implied by the ``path`` argument.The ``path`` argument may be a
    package-relative path, an absolute path, or a :term:`asset
    specification`. If a defname is defined, in the form of
    package:path/to/template#defname.mako, a function named ``defname``
    inside the template will then be rendered.
    """
    warnings = warnings # for testing

    def __init__(self, path, defname, lookup):
        self.path = path
        self.defname = defname
        self.lookup = lookup

    def implementation(self):
        return self.lookup.get_template(self.path)

    def __call__(self, value, system):
        context = system.pop('context', None)
        if context is not None:
            system['_context'] = context
        # tuple returned to be deprecated
        if isinstance(value, tuple):
            self.warnings.warn(
                'Using a tuple in the form (\'defname\', {}) to render a '
                'Mako partial will be deprecated in the future. Use a '
                'Mako template renderer as documented in the "Using A '
                'Mako def name Within a Renderer Name" chapter of the '
                'Pyramid narrative documentation instead',
                DeprecationWarning,
                3)
            self.defname, value = value
        try:
            system.update(value)
        except (TypeError, ValueError):
            raise ValueError('renderer was passed non-dictionary as value')
        template = self.implementation()
        if self.defname is not None:
            template = template.get_def(self.defname)
        try:
            result = template.render_unicode(**system)
        except:
            try:
                exc_info = sys.exc_info()
                errtext = text_error_template().render(
                    error=exc_info[1],
                    traceback=exc_info[2]
                    )
                reraise(MakoRenderingException(errtext), None, exc_info[2])
            finally:
                del exc_info

        return result

def parse_options_from_settings(settings, settings_prefix, maybe_dotted):
    """ Parse options for use with Mako's TemplateLookup from settings."""
    def sget(name, default=None):
        return settings.get(settings_prefix + name, default)

    reload_templates = settings.get('pyramid.reload_templates', None)
    if reload_templates is None:
        reload_templates = settings.get('reload_templates', False)
    reload_templates = asbool(reload_templates)
    directories = sget('directories', [])
    module_directory = sget('module_directory', None)
    input_encoding = sget('input_encoding', 'utf-8')
    error_handler = sget('error_handler', None)
    default_filters = sget('default_filters', 'h')
    imports = sget('imports', None)
    strict_undefined = asbool(sget('strict_undefined', False))
    preprocessor = sget('preprocessor', None)
    if not is_nonstr_iter(directories):
        directories = list(filter(None, directories.splitlines()))
    directories = [abspath_from_asset_spec(d) for d in directories]
    if module_directory is not None:
        module_directory = abspath_from_asset_spec(module_directory)
    if error_handler is not None:
        error_handler = maybe_dotted(error_handler)
    if default_filters is not None:
        if not is_nonstr_iter(default_filters):
            default_filters = list(filter(
                None, default_filters.splitlines()))
    if imports is not None:
        if not is_nonstr_iter(imports):
            imports = list(filter(None, imports.splitlines()))
    if preprocessor is not None:
        preprocessor = maybe_dotted(preprocessor)

    return dict(
        directories=directories,
        module_directory=module_directory,
        input_encoding=input_encoding,
        error_handler=error_handler,
        default_filters=default_filters,
        imports=imports,
        filesystem_checks=reload_templates,
        strict_undefined=strict_undefined,
        preprocessor=preprocessor,
    )

def add_mako_renderer(config, extension, settings_prefix='mako.'):
    """ Register a Mako renderer for a template extension.

    This function is available on the Pyramid configurator after
    including the package:

    .. code-block:: python

       config.add_mako_renderer('.html', settings_prefix='mako.')

    The renderer will load its configuration from a prefix in the Pyramid
    settings dictionary. The default prefix is 'mako.'.
    """
    renderer_factory = MakoRendererFactory()
    config.add_renderer(extension, renderer_factory)

    def register():
        registry = config.registry
        opts = parse_options_from_settings(
            registry.settings, settings_prefix, config.maybe_dotted)
        lookup = PkgResourceTemplateLookup(**opts)
        renderer_factory.lookup = lookup

    config.action(('mako-renderer', extension), register)

def includeme(config):
    """ Set up standard configurator registrations.  Use via:

    .. code-block:: python

       config = Configurator()
       config.include('pyramid_mako')

    Once this function has been invoked, the ``.mako`` and ``.mak`` renderers
    are available for use in Pyramid. This can be overridden and more may be
    added via the ``config.add_mako_renderer`` directive. See
    :func:`~pyramid_mako.add_mako_renderer` documentation for more information.
    """
    config.add_directive('add_mako_renderer', add_mako_renderer)

    config.add_mako_renderer('.mako')
    config.add_mako_renderer('.mak')
