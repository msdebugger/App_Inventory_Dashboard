from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Application,
    AuditLogEntry,
    Category,
    Department,
    Deployment,
    Environment,
    License,
    Tag,
    Vendor,
)

CRITICALITY_COLORS = {
    "LOW": "#6c757d",
    "MEDIUM": "#0d6efd",
    "HIGH": "#fd7e14",
    "CRITICAL": "#dc3545",
}

STATUS_COLORS = {
    "PLANNED": "#6c757d",
    "ACTIVE": "#198754",
    "DEPRECATED": "#fd7e14",
    "RETIRED": "#dc3545",
    "MAINTENANCE": "#0dcaf0",
}


class DeploymentInline(admin.TabularInline):
    model = Deployment
    extra = 0
    fields = ("environment", "server_name", "ip_address", "operating_system", "region", "is_active")


class LicenseInline(admin.TabularInline):
    model = License
    extra = 0
    fields = ("license_type", "seats_purchased", "seats_used", "purchase_date", "expiry_date", "cost")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "vendor",
        "department",
        "colored_status",
        "colored_criticality",
        "application_type",
        "hosting_type",
        "annual_cost",
        "is_business_critical",
    )
    list_filter = (
        "status",
        "criticality",
        "application_type",
        "hosting_type",
        "category",
        "department",
        "is_business_critical",
        "data_classification",
    )
    search_fields = ("name", "description", "owner_name", "owner_email", "vendor__name")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("category", "vendor", "department", "tags")
    date_hierarchy = "launch_date"
    inlines = [DeploymentInline, LicenseInline]
    readonly_fields = ("uuid", "created_at", "updated_at")
    fieldsets = (
        ("Basic Information", {
            "fields": ("name", "slug", "description", "category", "tags", "version")
        }),
        ("Ownership", {
            "fields": ("vendor", "department", "owner_name", "owner_email",
                       "technical_contact", "technical_contact_email")
        }),
        ("Classification", {
            "fields": ("application_type", "hosting_type", "status", "criticality",
                       "is_business_critical", "data_classification")
        }),
        ("Links", {
            "fields": ("url", "repository_url")
        }),
        ("Lifecycle", {
            "fields": ("launch_date", "end_of_life_date", "last_audit_date")
        }),
        ("Financials & SLA", {
            "fields": ("annual_cost", "uptime_sla")
        }),
        ("System", {
            "fields": ("uuid", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Status")
    def colored_status(self, obj):
        color = STATUS_COLORS.get(obj.status, "#6c757d")
        return format_html(
            '<span style="color:{}; font-weight:600;">{}</span>', color, obj.get_status_display()
        )

    @admin.display(description="Criticality")
    def colored_criticality(self, obj):
        color = CRITICALITY_COLORS.get(obj.criticality, "#6c757d")
        return format_html(
            '<span style="color:{}; font-weight:600;">{}</span>', color, obj.get_criticality_display()
        )


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ("name", "support_email", "support_phone", "account_manager", "application_count")
    search_fields = ("name", "support_email", "account_manager")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "description")
    search_fields = ("name",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "cost_center")
    search_fields = ("name", "code")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color")
    search_fields = ("name",)


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(Deployment)
class DeploymentAdmin(admin.ModelAdmin):
    list_display = ("application", "environment", "server_name", "ip_address", "region", "is_active")
    list_filter = ("environment", "is_active", "region")
    search_fields = ("application__name", "server_name", "ip_address")
    autocomplete_fields = ("application",)


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    list_display = ("application", "license_type", "seats_purchased", "seats_used", "expiry_date", "cost")
    list_filter = ("license_type",)
    search_fields = ("application__name", "license_key")
    autocomplete_fields = ("application",)


@admin.register(AuditLogEntry)
class AuditLogEntryAdmin(admin.ModelAdmin):
    list_display = ("application_name_snapshot", "action", "actor", "created_at")
    list_filter = ("action",)
    search_fields = ("application_name_snapshot", "notes")
    readonly_fields = ("created_at",)


admin.site.site_header = "Application Inventory System"
admin.site.site_title = "App Inventory Admin"
admin.site.index_title = "Inventory Management"
