from pyramid_debugtoolbar.panels import DebugPanel
from pyramid_debugtoolbar.compat import text_
from pyramid.interfaces import IRendererFactory
import pyramid_mako
_ = lambda x: x


class PyramidMakoMainDebugPanel(DebugPanel):
    """
    A panel to display HTTP request and response headers.
    """
    name = 'pyramid_mako'
    has_content = True
    template = 'pyramid_mako.debugtoolbar.panels:templates/main.dbtmako'
    title = _('PyramidMako')
    nav_title = title
    

    def __init__(self, request):
        self.registry = request.registry
        all_renderers = request.registry.getAllUtilitiesRegisteredFor(IRendererFactory)
        mako_renderers = [r for r in all_renderers if isinstance(r, pyramid_mako.MakoRendererFactory)]
        self.mako_renderers = mako_renderers
        self.data = {'mako_renderers': self.mako_renderers, }
