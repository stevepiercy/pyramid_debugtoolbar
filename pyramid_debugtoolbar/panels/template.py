from pyramid_debugtoolbar.panels import DebugPanel

_ = lambda x: x

class TemplateDebugPanel(DebugPanel):
    """
    Panel that displays the renderers used during the request.
    """
    name = 'Template'
    has_content = True

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.templates = []

    def process_beforerender(self, event):
        self.templates.append(event)

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass

    def nav_title(self):
        return _('Templates')

    def nav_subtitle(self):
        return "%d rendered" % len(self.templates)

    def title(self):
        return _('Templates')

    def url(self):
        return ''

    def content(self):
        return self.render('panels/template.jinja2', {
            'templates': self.templates
        })


