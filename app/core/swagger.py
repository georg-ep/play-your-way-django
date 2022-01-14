from rest_framework import permissions
from django.conf import settings

from drf_yasg.views import get_schema_view
from drf_yasg import openapi, generators


class HttpAndHttpsSchemaGenerator(generators.OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["https", "http"]
        return schema


def app_swagger_view(urls_patterns: tuple, title=None):
    """
    Returns swagger schema view for pretty API representation. Schema shows only methods accessible via url_patterns
    provided.
    :param urls_patterns: patterns from urls.py file
    :param title: optional title for the generated view
    :return: Swagger schema view
    """
    if title is None:
        title = 'API view'

    generator = None

    if settings.INCLUDE_HTTPS_SCHEMA:
        generator = HttpAndHttpsSchemaGenerator

    view = get_schema_view(
        openapi.Info(title=title, default_version='', ),
        public=True,
        permission_classes=(permissions.BasePermission,),
        patterns=urls_patterns,
        generator_class=generator
    )
    return view.with_ui('swagger')
