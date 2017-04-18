import unittest
from pyramid import testing

from pyramid_selectable_renderer import SelectableRendererSetup 
from pyramid_selectable_renderer.custom import ReceiveTemplatePathFormat
from pyramid_selectable_renderer.custom import SelectByRequestGen

dead_or_alive = SelectableRendererSetup(
    ReceiveTemplatePathFormat,
    SelectByRequestGen.generate(lambda x : x.matchdict.get("status", "???")),
    renderer_name = "dead_or_alive")

def dummy_renderer(info):
    return lambda value, system_value: u'%s: %s' % (info.name, value['name'])

class SelectableRendererIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.add_renderer('.dummy', dummy_renderer)

    def tearDown(self):
        testing.tearDown()

    def setup_view(self):
        def dummy_view(request):
            return {"name": request.matchdict["name"]}

        renderer = dead_or_alive("%s.dummy")
        self.config.add_view(dummy_view, name="dummy", renderer=renderer)

        def call_view(matchdict):
            from pyramid.view import render_view_to_response
            request = testing.DummyRequest(matchdict=matchdict)
            context = None
            return render_view_to_response(context, request, name="dummy")
        return call_view

        
    def test_render_result(self):
        dead_or_alive.register_to(self.config)
        call_view = self.setup_view()

        result = call_view(dict(name="foo", status="alive"))
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "alive.dummy: foo")

        result = call_view(dict(name="foo", status="dead"))
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "dead.dummy: foo")


    def test_BeforeRenderer_Event_call_times(self):
        dead_or_alive.register_to(self.config)
        call_view = self.setup_view()

        counter = [0]
        def count_event(event):
            counter[0] += 1

        from pyramid.events import BeforeRender
        self.config.add_subscriber(count_event, BeforeRender)

        self.assertEquals(counter[0], 0)
        call_view(dict(name="foo", status="dead"))
        self.assertEquals(counter[0], 1)
        call_view(dict(name="foo", status="alive"))
        self.assertEquals(counter[0], 2)

    def test_select_candidates_with_default(self):
        from pyramid_selectable_renderer.custom import ReceiveTemplatePathCandidatesDict
        from pyramid_selectable_renderer.custom import SelectByRequestGen

        dispatch_by_host = SelectableRendererSetup(
            ReceiveTemplatePathCandidatesDict,
            SelectByRequestGen.generate(lambda request : request.host),
            renderer_name = "dispatch_by_host")
        
        def dummy_view(request):
            return {"name": request.matchdict["name"]}

        renderer = dispatch_by_host({
                "Asite.com": "alive.dummy",
                }, default="dead.dummy")
        self.config.add_view(dummy_view, name="dispatch_by_host", renderer=renderer)

        def call_view(name, host=None):
            from pyramid.view import render_view_to_response
            request = testing.DummyRequest(host=host,matchdict=dict(name=name))
            context = None
            return render_view_to_response(context, request, name="dispatch_by_host")

        
        dispatch_by_host.register_to(self.config)

        result = call_view("foo", host="Asite.com")
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "alive.dummy: foo")

        result = call_view("foo", host="Csite.com")
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "dead.dummy: foo")

        
    #todo refactoring
    def test_2kinds_selectable_renderer_settings(self):
        dead_or_alive.register_to(self.config)
        call_view = self.setup_view()

        result = call_view(dict(name="foo", status="alive"))
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "alive.dummy: foo")

        ## add another kind selectable renderer

        from pyramid_selectable_renderer.custom import ReceiveTemplatePathCandidatesDict
        from pyramid_selectable_renderer.custom import SelectByRequestGen

        dispatch_by_host = SelectableRendererSetup(
            ReceiveTemplatePathCandidatesDict,
            SelectByRequestGen.generate(lambda request : request.host),
            renderer_name = "dispatch_by_host")
        
        def dummy_view(request):
            return {"name": request.matchdict["name"]}

        renderer = dispatch_by_host({
                "Asite.com": "alive.dummy",
                "Bsite.com": "dead.dummy",
                })
        self.config.add_view(dummy_view, name="dispatch_by_host", renderer=renderer)

        def call_view(name, host=None):
            from pyramid.view import render_view_to_response
            request = testing.DummyRequest(host=host,matchdict=dict(name=name))
            context = None
            return render_view_to_response(context, request, name="dispatch_by_host")

        
        dispatch_by_host.register_to(self.config)

        result = call_view("foo", host="Asite.com")
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "alive.dummy: foo")

        result = call_view("boo", host="Bsite.com")
        self.assertEquals(result.content_type, "text/html")
        self.assertEquals(result.body, "dead.dummy: boo")

if __name__ == "__main__":
    unittest.main()
