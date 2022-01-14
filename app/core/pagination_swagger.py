from drf_yasg.inspectors import PaginatorInspector
from drf_yasg import openapi

from collections import OrderedDict


# https://github.com/axnsan12/drf-yasg/issues/382 - circular import bug from drf_yasg when trying to subclass this
# subclass class in pagination_inspectors.py instead
class DefaultPagerInspector(PaginatorInspector):
    def get_paginated_response(self, paginator, response_schema):
        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=OrderedDict((
                ("count", openapi.Schema(type=openapi.TYPE_INTEGER)),
                ("next", openapi.Schema(type=openapi.TYPE_STRING)),
                ("previous", openapi.Schema(type=openapi.TYPE_STRING)),
                ("current", openapi.Schema(type=openapi.TYPE_INTEGER)),
                ("pages_count", openapi.Schema(type=openapi.TYPE_INTEGER)),
                ("page_size", openapi.Schema(type=openapi.TYPE_INTEGER)),
                ("results", response_schema)
            ))
        )
