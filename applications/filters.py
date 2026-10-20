import django_filters
from django import forms

from .models import Application, Category, Department, Vendor

SELECT_CLASSES = (
    "w-full rounded-lg border border-slate-300 dark:border-slate-600 "
    "bg-white dark:bg-[#1c2233] text-navy-700 dark:text-slate-100 text-sm "
    "px-3 py-2 focus:outline-none focus:ring-2 focus:ring-accent-500"
)
CHECKBOX_WRAPPER_CLASSES = "space-y-1 text-sm text-navy-700 dark:text-slate-200"


class ApplicationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains", label="Name contains")
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={"class": SELECT_CLASSES}),
    )
    vendor = django_filters.ModelChoiceFilter(
        queryset=Vendor.objects.all(),
        widget=forms.Select(attrs={"class": SELECT_CLASSES}),
    )
    department = django_filters.ModelChoiceFilter(
        queryset=Department.objects.all(),
        widget=forms.Select(attrs={"class": SELECT_CLASSES}),
    )
    status = django_filters.MultipleChoiceFilter(
        choices=Application.Status.choices,
        widget=forms.CheckboxSelectMultiple(attrs={"class": CHECKBOX_WRAPPER_CLASSES}),
    )
    criticality = django_filters.MultipleChoiceFilter(
        choices=Application.Criticality.choices,
        widget=forms.CheckboxSelectMultiple(attrs={"class": CHECKBOX_WRAPPER_CLASSES}),
    )
    application_type = django_filters.ChoiceFilter(
        choices=Application.AppType.choices,
        widget=forms.Select(attrs={"class": SELECT_CLASSES}),
    )
    hosting_type = django_filters.ChoiceFilter(
        choices=Application.HostingType.choices,
        widget=forms.Select(attrs={"class": SELECT_CLASSES}),
    )
    is_business_critical = django_filters.BooleanFilter(
        widget=forms.Select(
            choices=[("", "Any"), (True, "Yes"), (False, "No")],
            attrs={"class": SELECT_CLASSES},
        )
    )
    min_cost = django_filters.NumberFilter(field_name="annual_cost", lookup_expr="gte", label="Min annual cost")
    max_cost = django_filters.NumberFilter(field_name="annual_cost", lookup_expr="lte", label="Max annual cost")

    class Meta:
        model = Application
        fields = [
            "name", "category", "vendor", "department", "status",
            "criticality", "application_type", "hosting_type", "is_business_critical",
        ]
