from django.contrib.admin import SimpleListFilter

class BalanceFilter(SimpleListFilter):
    title = 'Balance'
    parameter_name = 'balance_range'

    def lookups(self, request, model_admin):
        return [
            ('<1000000', '< 1,000,000'),
            ('1000000-10000000', '1,000,000 - 10,000,000'),
            ('>10000000', '> 10,000,000'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '<1000000':
            return queryset.filter(balance__lt=1000000)
        if self.value() == '1000000-10000000':
            return queryset.filter(balance__gte=1000000, balance__lte=10000000)
        if self.value() == '>10000000':
            return queryset.filter(balance__gt=10000000)
        return queryset


class PhoneFilter(SimpleListFilter):
    title = 'Phone'
    parameter_name = 'has_phone'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'Has phone'),
            ('no', 'No phone'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(phone__isnull=True).exclude(phone__exact='')
        if self.value() == 'no':
            return queryset.filter(phone__isnull=True) | queryset.filter(phone__exact='')
        return queryset


class ExpireYearFilter(SimpleListFilter):
    title = 'Expire Year'
    parameter_name = 'expire_year'

    def lookups(self, request, model_admin):
        return [(str(y), str(y)) for y in range(24, 29)]  # 2024-2028

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(expire__contains=self.value())
        return queryset

