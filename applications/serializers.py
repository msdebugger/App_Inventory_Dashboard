from rest_framework import serializers

from .models import (
    Application, Category, Department, Deployment, Environment, License, Tag, Vendor,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description", "icon"]


class VendorSerializer(serializers.ModelSerializer):
    application_count = serializers.ReadOnlyField()

    class Meta:
        model = Vendor
        fields = [
            "id", "name", "website", "support_email", "support_phone",
            "account_manager", "notes", "application_count",
        ]


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "code", "cost_center"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "color"]


class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environment
        fields = ["id", "name"]


class DeploymentSerializer(serializers.ModelSerializer):
    environment_name = serializers.CharField(source="environment.get_name_display", read_only=True)

    class Meta:
        model = Deployment
        fields = [
            "id", "application", "environment", "environment_name", "server_name", "ip_address",
            "operating_system", "cpu_cores", "ram_gb", "storage_gb", "region", "is_active",
        ]


class LicenseSerializer(serializers.ModelSerializer):
    is_expired = serializers.ReadOnlyField()
    seats_available = serializers.ReadOnlyField()

    class Meta:
        model = License
        fields = [
            "id", "application", "license_type", "license_key", "seats_purchased",
            "seats_used", "seats_available", "purchase_date", "expiry_date", "cost", "is_expired",
        ]


class ApplicationListSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    vendor = serializers.StringRelatedField()
    department = serializers.StringRelatedField()

    class Meta:
        model = Application
        fields = [
            "id", "uuid", "name", "slug", "category", "vendor", "department",
            "status", "criticality", "application_type", "hosting_type",
            "annual_cost", "is_business_critical",
        ]


class ApplicationDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    vendor = VendorSerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    deployments = DeploymentSerializer(many=True, read_only=True)
    licenses = LicenseSerializer(many=True, read_only=True)
    is_end_of_life_soon = serializers.ReadOnlyField()

    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source="category", write_only=True
    )
    vendor_id = serializers.PrimaryKeyRelatedField(
        queryset=Vendor.objects.all(), source="vendor", write_only=True, required=False, allow_null=True
    )
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source="department", write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Application
        fields = [
            "id", "uuid", "name", "slug", "description",
            "category", "category_id", "vendor", "vendor_id", "department", "department_id", "tags",
            "owner_name", "owner_email", "technical_contact", "technical_contact_email",
            "version", "application_type", "hosting_type", "status", "criticality",
            "url", "repository_url",
            "launch_date", "end_of_life_date", "last_audit_date",
            "annual_cost", "uptime_sla", "is_business_critical", "data_classification",
            "is_end_of_life_soon", "deployments", "licenses",
            "created_at", "updated_at",
        ]
        read_only_fields = ["uuid", "slug", "created_at", "updated_at"]
