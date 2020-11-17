from django.db import models
from django.db.models.constants import LOOKUP_SEP
from rest_framework.filters import SearchFilter


class CustomSearchFilter(SearchFilter):
    """
    Need to re-implement SearchFilter because 'unaccent' feature is not supported.
    """

    lookup_sufixes = [
        'unaccent'
    ]

    def get_search_fields(self, view, request):
        """
        Append '__unaccent' to all search fields.
        """
        search_fields = super(CustomSearchFilter, self).get_search_fields(view, request)

        if search_fields:
            return [search_field + '__unaccent' for search_field in search_fields]

        return search_fields

    def must_call_distinct(self, queryset, search_fields):
        """
        Return True if 'distinct()' should be used to query the given lookups.
        """
        for search_field in search_fields:
            opts = queryset.model._meta
            if search_field[0] in self.lookup_prefixes:
                search_field = search_field[1:]
            # Annotated fields do not need to be distinct
            if isinstance(queryset, models.QuerySet) and search_field in queryset.query.annotations:
                return False
            parts = search_field.split(LOOKUP_SEP)
            for part in parts:
                # This line is to fix a bug for unaccent
                if part in self.lookup_sufixes:
                    return False

                field = opts.get_field(part)
                if hasattr(field, 'get_path_info'):
                    # This field is a relation, update opts to follow the relation
                    path_info = field.get_path_info()
                    opts = path_info[-1].to_opts
                    if any(path.m2m for path in path_info):
                        # This field is a m2m relation so we know we need to call distinct
                        return True
        return False
