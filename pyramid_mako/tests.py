## come on python gimme some of that sweet, sweet -*- coding: utf-8 -*-

import shutil
import tempfile
import unittest

from pyramid import testing

from pyramid.compat import (
    text_,
    text_type,
    )

class Base(object):
    def setUp(self):
        self.config = testing.setUp()
        self.config.begin()
        import os
        here = os.path.abspath(os.path.dirname(__file__))
        self.templates_dir = os.path.join(here, 'fixtures')

    def tearDown(self):
        self.config.end()

class TestMakoRendererFactory(Base, unittest.TestCase):
    def _getTargetClass(self):
        from pyramid_mako import MakoRendererFactory
        return MakoRendererFactory

    def _makeOne(self, lookup):
        factory = self._getTargetClass()()
        factory.lookup = lookup
        return factory

    def _callFUT(self, info, lookup=None):
        factory = self._makeOne(lookup)
        return factory(info)

    def _makeRendererInfo(self, spec, **kw):
        opts = {
            'name': spec,
            'package': None,
            'registry': self.config.registry,
            'settings': self.config.get_settings(),
            'type': ''
        }
        opts.update(kw)
        return DummyRendererInfo(opts)

    def test_asset_spec_filenames(self):
        info = self._makeRendererInfo('app:moon-and-world.mak')
        renderer = self._callFUT(info)
        self.assertEqual(renderer.path, 'app:moon-and-world.mak')
        self.assertTrue(renderer.defname is None)

    def test_asset_spec_filenames_with_def(self):
        info = self._makeRendererInfo('app:moon-and-world#def.mak')
        renderer = self._callFUT(info)
        self.assertEqual(renderer.path, 'app:moon-and-world.mak')
        self.assertEqual(renderer.defname, 'def')

    def test_asset_spec_subfolder_filenames(self):
        info = self._makeRendererInfo(
            'pyramid_mako.tests:fixtures/helloworld.mak')
        renderer = self._callFUT(info)
        self.assertEqual(renderer.path,
                         'pyramid_mako.tests:fixtures/helloworld.mak')
        self.assertTrue(renderer.defname is None)

    def test_asset_spec_subfolder_filenames_with_def(self):
        info = self._makeRendererInfo(
            'pyramid_mako.tests:fixtures/helloworld#def.mak')
        renderer = self._callFUT(info)
        self.assertEqual(renderer.path,
                         'pyramid_mako.tests:fixtures/helloworld.mak')
        self.assertEqual(renderer.defname, 'def')

    def test_relative_filenames(self):
        info = self._makeRendererInfo('templates/moon-and-world.mak')
        renderer = self._callFUT(info)
        self.assertEqual(renderer.path, 'templates/moon-and-world.mak')
        self.assertTrue(renderer.defname is None)

    def test_relative_filenames_with_def(self):
        info = self._makeRendererInfo('templates/moon-and-world#def.mak')
        renderer = self._callFUT(info)
        self.assertEqual(renderer.path, 'templates/moon-and-world.mak')
        self.assertEqual(renderer.defname, 'def')

    def test_multiple_dotted_filenames(self):
        info = self._makeRendererInfo('moon.and.world.mak')
        renderer = self._callFUT(info)
        self.assertEqual(renderer.path, 'moon.and.world.mak')
        self.assertTrue(renderer.defname is None)

    def test_multiple_dotted_filenames_with_def(self):
        info = self._makeRendererInfo('moon.and.world#def.mak')
        renderer = self._callFUT(info)
        self.assertEqual(renderer.path, 'moon.and.world.mak')
        self.assertEqual(renderer.defname, 'def')

    def test_space_dot_name(self):
        info = self._makeRendererInfo('hello .world.mako')
        renderer = self._callFUT(info)
        self.assertEqual(renderer.path, 'hello .world.mako')
        self.assertTrue(renderer.defname is None)

    def test_space_dot_name_with_def(self):
        info = self._makeRendererInfo('hello .world#comp.mako')
        renderer = self._callFUT(info)
        self.assertEqual(renderer.path, 'hello .world.mako')
        self.assertEqual(renderer.defname, 'comp')

class Test_parse_options_from_settings(Base, unittest.TestCase):
    def _callFUT(self, settings, settings_prefix='mako.'):
        from pyramid_mako import parse_options_from_settings
        return parse_options_from_settings(settings, settings_prefix,
                                           self.config.maybe_dotted)

    def test_no_directories(self):
        result = self._callFUT({})
        self.assertEqual(result['directories'], [])
        self.assertEqual(result['filesystem_checks'], False)

    def test_directories_path(self):
        settings = {'mako.directories': self.templates_dir}
        result = self._callFUT(settings)
        self.assertEqual(result['directories'], [self.templates_dir])
        self.assertEqual(result['filesystem_checks'], False)

    def test_composite_directories_path(self):
        twice = '\n' + self.templates_dir + '\n' + self.templates_dir + '\n'
        settings = {'mako.directories': twice}
        result = self._callFUT(settings)
        self.assertEqual(result['directories'], [self.templates_dir] * 2)

    def test_directories_list(self):
        import sys
        import os.path
        settings = {'mako.directories': ['a', 'b']}
        result = self._callFUT(settings)
        module_path = os.path.dirname(
            sys.modules['__main__'].__file__).rstrip('.') # ./setup.py
        self.assertEqual(result['directories'], [
            os.path.join(module_path, 'a'),
            os.path.join(module_path, 'b')])

    def test_with_module_directory_asset_spec(self):
        import os
        module_directory = 'pyramid_mako.tests:fixtures'
        settings = {'mako.directories': self.templates_dir,
                    'mako.module_directory': module_directory}
        result = self._callFUT(settings)
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.assertEqual(result['module_directory'], fixtures)

    def test_with_module_directory_asset_abspath(self):
        import os
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        settings = {'mako.directories': self.templates_dir,
                    'mako.module_directory': fixtures}
        result = self._callFUT(settings)
        self.assertEqual(result['module_directory'], fixtures)

    def test_with_input_encoding(self):
        settings = {'mako.directories': self.templates_dir,
                    'mako.input_encoding': 'utf-16'}
        result = self._callFUT(settings)
        self.assertEqual(result['input_encoding'], 'utf-16')

    def test_with_error_handler(self):
        import pyramid_mako.tests
        settings = {'mako.directories': self.templates_dir,
                    'mako.error_handler': 'pyramid_mako.tests'}
        result = self._callFUT(settings)
        self.assertEqual(result['error_handler'], pyramid_mako.tests)

    def test_with_preprocessor(self):
        import pyramid_mako.tests
        settings = {'mako.directories': self.templates_dir,
                    'mako.preprocessor': 'pyramid_mako.tests'}
        result = self._callFUT(settings)
        self.assertEqual(result['preprocessor'], pyramid_mako.tests)

    def test_with_default_filters(self):
        settings = {'mako.directories': self.templates_dir,
                    'mako.default_filters': '\nh\ng\n\n'}
        result = self._callFUT(settings)
        self.assertEqual(result['default_filters'], ['h', 'g'])

    def test_with_default_filters_list(self):
        settings = {'mako.directories': self.templates_dir,
                    'mako.default_filters': ['h', 'g']}
        result = self._callFUT(settings)
        self.assertEqual(result['default_filters'], ['h', 'g'])

    def test_with_imports(self):
        settings = {'mako.directories': self.templates_dir,
                    'mako.imports': '\none\ntwo\n\n'}
        result = self._callFUT(settings)
        self.assertEqual(result['imports'], ['one', 'two'])

    def test_with_imports_list(self):
        settings = {'mako.directories': self.templates_dir,
                    'mako.imports': ['one', 'two']}
        result = self._callFUT(settings)
        self.assertEqual(result['imports'], ['one', 'two'])

    def test_with_strict_undefined_true(self):
        settings = {'mako.directories': self.templates_dir,
                    'mako.strict_undefined': 'true'}
        result = self._callFUT(settings)
        self.assertEqual(result['strict_undefined'], True)

    def test_with_strict_undefined_false(self):
        settings = {'mako.directories': self.templates_dir,
                    'mako.strict_undefined': 'false'}
        result = self._callFUT(settings)
        self.assertEqual(result['strict_undefined'], False)

    def test_reload_templates_namespace(self):
        settings = {'mako.directories': self.templates_dir,
                    'pyramid.reload_templates': True}
        result = self._callFUT(settings)
        self.assertEqual(result['filesystem_checks'], True)

    def test_reload_templates_namespace_text(self):
        settings = {'mako.directories': self.templates_dir,
                    'pyramid.reload_templates': 'True'}
        result = self._callFUT(settings)
        self.assertEqual(result['filesystem_checks'], True)

    def test_multiple_registration_different_name(self):
        import os.path
        import sys
        settings = {'mako.directories': 'a\n\nb',
                    'othermako.directories': 'c\n\nd',
                    'pyramid.reload_templates': 'true'}
        result = self._callFUT(settings)
        module_path = os.path.dirname(
            sys.modules['__main__'].__file__).rstrip('.') # ./setup.py
        self.assertEqual(result['directories'], [
            os.path.join(module_path, 'a'),
            os.path.join(module_path, 'b')])

        result = self._callFUT(settings, settings_prefix='othermako.')
        self.assertEqual(result['directories'], [
            os.path.join(module_path, 'c'),
            os.path.join(module_path, 'd')])

class MakoLookupTemplateRendererTests(Base, unittest.TestCase):
    def _getTargetClass(self):
        from pyramid_mako import MakoLookupTemplateRenderer
        return MakoLookupTemplateRenderer

    def _makeOne(self, *arg, **kw):
        klass = self._getTargetClass()
        return klass(*arg, **kw)

    def test_call(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', None, lookup)
        result = instance({}, {'system': 1})
        self.assertTrue(isinstance(result, text_type))
        self.assertEqual(result, text_('result'))

    def test_call_with_system_context(self):
        # lame
        lookup = DummyLookup()
        instance = self._makeOne('path', None, lookup)
        result = instance({}, {'context': 1})
        self.assertTrue(isinstance(result, text_type))
        self.assertEqual(result, text_('result'))
        self.assertEqual(lookup.values, {'_context': 1})

    def test_call_with_tuple_value(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', None, lookup)
        warnings = DummyWarnings()
        instance.warnings = warnings
        result = instance(('fub', {}), {'context': 1})
        self.assertEqual(lookup.deffed, 'fub')
        self.assertEqual(result, text_('result'))
        self.assertEqual(lookup.values, {'_context': 1})
        self.assertEqual(len(warnings.msgs), 1)

    def test_call_with_defname(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', 'defname', lookup)
        result = instance({}, {'system': 1})
        self.assertTrue(isinstance(result, text_type))
        self.assertEqual(result, text_('result'))

    def test_call_with_defname_with_tuple_value(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', 'defname', lookup)
        warnings = DummyWarnings()
        instance.warnings = warnings
        result = instance(('defname', {}), {'context': 1})
        self.assertEqual(lookup.deffed, 'defname')
        self.assertEqual(result, text_('result'))
        self.assertEqual(lookup.values, {'_context': 1})
        self.assertEqual(len(warnings.msgs), 1)

    def test_call_with_defname_with_tuple_value_twice(self):
        lookup = DummyLookup()
        instance1 = self._makeOne('path', 'defname', lookup)
        warnings = DummyWarnings()
        instance1.warnings = warnings
        result1 = instance1(('defname1', {}), {'context': 1})
        self.assertEqual(lookup.deffed, 'defname1')
        self.assertEqual(result1, text_('result'))
        self.assertEqual(lookup.values, {'_context': 1})
        instance2 = self._makeOne('path', 'defname', lookup)
        warnings = DummyWarnings()
        instance2.warnings = warnings
        result2 = instance2(('defname2', {}), {'context': 2})
        self.assertNotEqual(lookup.deffed, 'defname1')
        self.assertEqual(lookup.deffed, 'defname2')
        self.assertEqual(result2, text_('result'))
        self.assertEqual(lookup.values, {'_context': 2})

    def test_call_with_nondict_value(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', None, lookup)
        self.assertRaises(ValueError, instance, None, {})

    def test_call_render_raises(self):
        from pyramid_mako import MakoRenderingException
        lookup = DummyLookup(exc=NotImplementedError)
        instance = self._makeOne('path', None, lookup)
        try:
            instance({}, {})
        except MakoRenderingException as e:
            self.assertTrue('NotImplementedError' in e.text)
        else: # pragma: no cover
            raise AssertionError

    def test_implementation(self):
        lookup = DummyLookup()
        instance = self._makeOne('path', None, lookup)
        result = instance.implementation().render_unicode()
        self.assertTrue(isinstance(result, text_type))
        self.assertEqual(result, text_('result'))

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.add_settings({'mako.directories':
                                  'pyramid_mako.tests:fixtures'})
        self.config.include('pyramid_mako')

    def tearDown(self):
        self.config.end()

    def test_render(self):
        from pyramid.renderers import render
        result = render('helloworld.mak', {'a': 1}).replace('\r', '')
        self.assertEqual(result, text_('\nHello föö\n', 'utf-8'))

    def test_render_from_fs(self):
        from pyramid.renderers import render
        result = render('helloworld.mak', {'a': 1}).replace('\r', '')
        self.assertEqual(result, text_('\nHello föö\n', 'utf-8'))

    def test_render_inheritance(self):
        from pyramid.renderers import render
        result = render('helloinherit.mak', {}).replace('\r', '')
        self.assertEqual(result, text_('Layout\nHello World!\n'))

    def test_render_inheritance_pkg_spec(self):
        from pyramid.renderers import render
        result = render('hello_inherit_pkg.mak', {}).replace('\r', '')
        self.assertEqual(result, text_('Layout\nHello World!\n\n'))

    def test_render_namespace(self):
        from pyramid.renderers import render
        result = render('hellocompo.mak', {}).replace('\r', '')
        self.assertEqual(result, text_('\nNamespace\nHello \nWorld!\n\n'))

    def test_render_to_response(self):
        from pyramid.renderers import render_to_response
        result = render_to_response('helloworld.mak', {'a': 1})
        self.assertEqual(result.ubody.replace('\r', ''),
                         text_('\nHello föö\n', 'utf-8'))

    def test_render_to_response_pkg_spec(self):
        from pyramid.renderers import render_to_response
        result = render_to_response(
            'pyramid_mako.tests:fixtures/helloworld.mak', {'a': 1})
        self.assertEqual(result.ubody.replace('\r', ''),
                         text_('\nHello föö\n', 'utf-8'))

    def test_render_with_abs_path(self):
        from pyramid.renderers import render
        result = render('/helloworld.mak', {'a': 1}).replace('\r', '')
        self.assertEqual(result, text_('\nHello föö\n', 'utf-8'))

    def test_get_renderer(self):
        from pyramid.renderers import get_renderer
        result = get_renderer('helloworld.mak')
        self.assertEqual(
            result.implementation().render_unicode().replace('\r', ''),
            text_('\nHello föö\n', 'utf-8'))

    def test_template_not_found(self):
        from pyramid.renderers import render
        from mako.exceptions import TemplateLookupException
        self.assertRaises(TemplateLookupException, render,
                          'helloworld_not_here.mak', {})

    def test_template_default_escaping(self):
        from pyramid.renderers import render
        result = render('nonminimal.mak',
                        {'name': '<b>fred</b>'}).replace('\r', '')
        self.assertEqual(result, text_('Hello, &lt;b&gt;fred&lt;/b&gt;!\n'))

    def test_add_mako_renderer(self):
        from pyramid.renderers import render
        self.config.add_settings({'foo.directories':
                                  'pyramid_mako.tests:fixtures'})
        self.config.add_mako_renderer('.foo', settings_prefix='foo.')
        result = render('nonminimal.foo',
                        {'name': '<b>fred</b>'}).replace('\r', '')
        self.assertEqual(result, text_('Hello, &lt;b&gt;fred&lt;/b&gt;!\n'))

    def test_add_mako_renderer_before_settings(self):
        from pyramid.renderers import render
        config = testing.setUp(autocommit=False)
        config.include('pyramid_mako')
        config.add_mako_renderer('.foo', settings_prefix='foo.')
        config.add_settings({'foo.directories':
                             'pyramid_mako.tests:fixtures'})
        config.commit()
        result = render('nonminimal.foo',
                        {'name': '<b>fred</b>'}).replace('\r', '')
        self.assertEqual(result, text_('Hello, &lt;b&gt;fred&lt;/b&gt;!\n'))
        config.end()

class TestPkgResourceTemplateLookup(unittest.TestCase):
    def _makeOne(self, **kw):
        from pyramid_mako import PkgResourceTemplateLookup
        return PkgResourceTemplateLookup(**kw)

    def get_fixturedir(self):
        import os
        import pyramid_mako.tests
        return os.path.join(os.path.dirname(pyramid_mako.tests.__file__),
                            'fixtures')

    def test_adjust_uri_not_asset_spec(self):
        inst = self._makeOne()
        result = inst.adjust_uri('a', None)
        self.assertEqual(result, '/a')

    def test_adjust_uri_asset_spec(self):
        inst = self._makeOne()
        result = inst.adjust_uri('a:b', None)
        self.assertEqual(result, 'a:b')

    def test_adjust_uri_asset_spec_with_modified_asset_spec(self):
        inst = self._makeOne()
        result = inst.adjust_uri('a$b', None)
        self.assertEqual(result, 'a:b')

    def test_adjust_uri_not_asset_spec_with_relativeto_asset_spec(self):
        inst = self._makeOne()
        result = inst.adjust_uri('c', 'a:b')
        self.assertEqual(result, 'a:c')

    def test_adjust_uri_not_asset_spec_with_relativeto_modified_asset_spec(self):
        inst = self._makeOne()
        result = inst.adjust_uri('c', 'a$b')
        self.assertEqual(result, 'a:c')

    def test_adjust_uri_not_asset_spec_with_relativeto_not_asset_spec(self):
        inst = self._makeOne()
        result = inst.adjust_uri('b', '../a')
        self.assertEqual(result, '../b')

    def test_adjust_uri_not_asset_spec_abs_with_relativeto_asset_spec(self):
        inst = self._makeOne()
        result = inst.adjust_uri('/c', 'a:b')
        self.assertEqual(result, '/c')

    def test_adjust_uri_asset_spec_with_relativeto_not_asset_spec_abs(self):
        inst = self._makeOne()
        result = inst.adjust_uri('a:b', '/c')
        self.assertEqual(result, 'a:b')

    def test_get_template_not_asset_spec(self):
        fixturedir = self.get_fixturedir()
        inst = self._makeOne(directories=[fixturedir])
        result = inst.get_template('helloworld.mak')
        self.assertFalse(result is None)

    def test_get_template_asset_spec_with_filesystem_checks(self):
        inst = self._makeOne(filesystem_checks=True)
        result = inst.get_template(
            'pyramid_mako.tests:fixtures/helloworld.mak')
        self.assertFalse(result is None)

    def test_get_template_asset_spec_with_module_dir(self):
        tmpdir = tempfile.mkdtemp()
        try:
            inst = self._makeOne(module_directory=tmpdir)
            result = inst.get_template(
                'pyramid_mako.tests:fixtures/helloworld.mak')
            self.assertFalse(result is None)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_get_template_asset_spec_missing(self):
        from mako.exceptions import TopLevelLookupException
        fixturedir = self.get_fixturedir()
        inst = self._makeOne(filesystem_checks=True, directories=[fixturedir])
        self.assertRaises(TopLevelLookupException, inst.get_template,
                          'pyramid_mako.tests:fixtures/notthere.mak')

class TestMakoRenderingException(unittest.TestCase):
    def _makeOne(self, text):
        from pyramid_mako import MakoRenderingException
        return MakoRenderingException(text)

    def test_repr_and_str(self):
        exc = self._makeOne('text')
        self.assertEqual(str(exc), 'text')
        self.assertEqual(repr(exc), 'text')

class DummyLookup(object):
    def __init__(self, exc=None):
        self.exc = exc

    def get_template(self, path):
        self.path = path
        return self

    def get_def(self, path):
        self.deffed = path
        return self

    def render_unicode(self, **values):
        if self.exc:
            raise self.exc
        self.values = values
        return text_('result')

class DummyRendererInfo(object):
    def __init__(self, kw):
        self.__dict__.update(kw)


class DummyWarnings(object):
    def __init__(self):
        self.msgs = []
    def warn(self, msg, typ, level):
        self.msgs.append(msg)
