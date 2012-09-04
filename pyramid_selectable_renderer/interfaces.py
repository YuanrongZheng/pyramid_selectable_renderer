from zope.interface import Interface

class ISelectableRendererSelector(Interface):
    def __call__(vals, system_vals, request=None):
        pass
