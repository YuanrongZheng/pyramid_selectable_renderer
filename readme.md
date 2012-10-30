this is dirty implementation.

## how to use

* define selectable renderer.
** using selectable renderer as renderer factory
** using selectable renderer with view_config settings

### sample

    ## define selectable renderer
    from pyramid_selectable_renderer import SelectableRendererSetup 
    from pyramid_selectable_renderer.custom import RecieveTemplatePathCandidatesDict
    from pyramid_selectable_renderer.custom import SelectByRetvalLeftGen

    ValidateTrueOrNot = SelectableRendererSetup(
        RecieveTemplatePathCandidatesDict,
        SelectByRetvalLeftGen.generate(lambda x : x),
        renderer_name = "validate_true_or_not")

    ## in __init__.py
    def includeme(config):
        ValidateTrueOrNot.register_to(config) # enable to use selectable renderer

    ## in view.py
    @view_config(route_name="sample.confirm", ValidateTrueOrNot({True: "foo:success.pt", False: "foo:failure.pt"}))
    def form_confirm_view(context, request):
        form = ValidateForm(request.POST):
        return form.validate(), {"form": form}
    
