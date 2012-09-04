import unittest
from pyramid import testing
from zope.interface import implementer
from pyramid_selectable_renderer.interfaces import ISelectableRendererSelector

@implementer(ISelectableRendererSelector)
def dummy_selector(helper, val, system_vals, request=None):
    return helper.format_string % val

class SelectableRendererIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_lookup(self):
        self.config.include("pyramid_selectable_renderer")
        self.config.add_selectable_renderer_selector(dummy_selector)

        result = self.config.registry.getUtility(ISelectableRendererSelector)
        self.assertEquals(result, dummy_selector)
        
    def test_render_result(self):
        self.config.include("pyramid_selectable_renderer")
        self.config.add_selectable_renderer_selector(dummy_selector)
        from pyramid_selectable_renderer import selectable_renderer        

        def dummy_view(request):
            return {"template": request.matchdict["cond"], 
                    "name": request.matchdict["name"]}

        renderer = selectable_renderer("pyramid_selectable_renderer:%(template)s.mako")
        self.config.add_view(dummy_view, name="dummy", renderer=renderer)

        def call_view(matchdict):
            from pyramid.view import render_view_to_response
            request = testing.DummyRequest(matchdict=matchdict)
            context = None
            return render_view_to_response(context, request, name="dummy")

        result = call_view(dict(name="foo", cond="success"))
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "success: foo")

        result = call_view(dict(name="foo", cond="failure"))
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "failure: foo")

if __name__ == "__main__":
    unittest.main()
