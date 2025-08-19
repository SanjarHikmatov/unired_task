from django.contrib import admin
from django.http import HttpRequest
from django.db.models import QuerySet
from django.contrib.admin import SimpleListFilter


class BalanceFilter(SimpleListFilter):
    """
        Purpose:
            A custom Django Admin filter that allows filtering records
            based on predefined balance ranges.

        Attributes:
            title (str): The display name of the filter in the Django admin sidebar.
            parameter_name (str): The name of the query parameter used in the URL.

        Methods:
            lookups(request, model_admin):
                Returns a list of balance range options to be displayed in the sidebar.

            queryset(request, queryset):
                Filters the queryset based on the selected balance range.
    """
    title: str = 'Balance'
    parameter_name: str = 'balance_range'

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin) -> list[tuple[str, str]]:
        """
            Defines the available filter options.

            Args:
                request (HttpRequest): The current HTTP request object.
                model_admin (ModelAdmin): The admin class of the current model.

            Returns:
                list[tuple[str, str]]: A list of tuples containing the option key and display label.
        """
        return [
            ('<1000000', '< 1,000,000'),
            ('1000000-10000000', '1,000,000 - 10,000,000'),
            ('>10000000', '> 10,000,000'),
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet | None:
        """
            Filters the queryset according to the selected balance range.

            Args:
                request (HttpRequest): The current HTTP request object.
                queryset (QuerySet): The current queryset to filter.

            Returns:
                QuerySet | None: Filtered queryset or the original queryset if no filter is applied.
        """
        if self.value() == '<1000000':
            return queryset.filter(balance__lt=1000000)
        if self.value() == '1000000-10000000':
            return queryset.filter(balance__gte=1000000, balance__lte=10000000)  # Between 1M and 10M
        if self.value() == '>10000000':
            return queryset.filter(balance__gt=10000000)
        return queryset


class PhoneFilter(SimpleListFilter):
    """
        Purpose:
            A custom Django Admin filter that checks whether objects have a phone number.

        Attributes:
            title (str): The display name of the filter in the Django admin sidebar.
            parameter_name (str): The name of the query parameter used in the URL.

        Methods:
            lookups(request, model_admin):
                Defines the "Has phone" and "No phone" filter options.

            queryset(request, queryset):
                Filters objects depending on phone availability.
    """
    title: str = 'Phone'
    parameter_name: str = 'has_phone'

    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin) -> list[tuple[str, str]]:
        """
            Defines the available filter options.

            Args:
                request (HttpRequest): The current HTTP request object.
                model_admin (ModelAdmin): The admin class of the current model.

            Returns:
                list[tuple[str, str]]: A list of tuples for filter choices.
        """
        return [
            ('yes', 'Has phone'),
            ('no', 'No phone'),
        ]

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet | None:
        """
            Filters the queryset based on whether a phone number is present.

            Args:
                request (HttpRequest): The current HTTP request object.
                queryset (QuerySet): The current queryset to filter.

            Returns:
                QuerySet | None: Filtered queryset or the original queryset if no filter is applied.
        """
        if self.value() == 'yes':
            return queryset.exclude(phone__isnull=True).exclude(phone__exact='')
        if self.value() == 'no':
            return queryset.filter(phone__isnull=True) | queryset.filter(phone__exact='')
        return queryset


class ExpireYearFilter(SimpleListFilter):
    """
        Purpose:
            A custom Django Admin filter to filter records based on the card expiration year.

        Attributes:
            title (str): The display name of the filter in the Django admin sidebar.
            parameter_name (str): The name of the query parameter used in the URL.

        Methods:
            lookups(request, model_admin):
                Generates a list of expiration year options.

            queryset(request, queryset):
                Filters records that contain the chosen expiration year in the `expire` field.
    """
    title: str = 'Expire Year'
    parameter_name: str = 'expire_year'


    def lookups(self, request: HttpRequest, model_admin: admin.ModelAdmin) -> list[tuple[str, str]]:
        """
            Defines the available filter options for expiration years.

            Args:
                request (HttpRequest): The current HTTP request object.
                model_admin (ModelAdmin): The admin class of the current model.

            Returns:
                list[tuple[str, str]]: A list of expiration years (2024–2028).
        """
        return [(str(y), str(y)) for y in range(24, 29)]  # Expiration years: 2024-2028

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet | None:
        """
            Filters the queryset according to the selected expiration year.

            Args:
                request (HttpRequest): The current HTTP request object.
                queryset (QuerySet): The current queryset to filter.

            Returns:
                QuerySet | None: Filtered queryset or the original queryset if no filter is applied.
        """
        if self.value():
            return queryset.filter(expire__contains=self.value())
        return queryset
