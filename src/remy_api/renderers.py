from rest_framework.renderers import BrowsableAPIRenderer


class CustomBrowsableAPIRenderer(BrowsableAPIRenderer):

    def get_context(self, data, accepted_media_type, renderer_context):
        context = super().get_context(data, accepted_media_type, renderer_context)
        context['description'] = ''
        return context
