from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count

from .models import Application, Category, Department, Deployment, Environment, License, Tag, Vendor
from .serializers import (
    ApplicationDetailSerializer, ApplicationListSerializer, CategorySerializer,
    DepartmentSerializer, DeploymentSerializer, EnvironmentSerializer, LicenseSerializer,
    TagSerializer, VendorSerializer,
)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.select_related("category", "vendor", "department").prefetch_related(
        "tags", "deployments", "licenses"
    )
    lookup_field = "slug"
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["status", "criticality", "application_type", "hosting_type", "category", "department", "vendor"]
    search_fields = ["name", "description", "owner_name", "owner_email"]
    ordering_fields = ["name", "annual_cost", "launch_date", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return ApplicationListSerializer
        return ApplicationDetailSerializer

    @action(detail=False, methods=["get"])
    def stats(self, request):
        qs = self.get_queryset()
        data = {
            "total_applications": qs.count(),
            "total_annual_cost": qs.aggregate(total=Sum("annual_cost"))["total"] or 0,
            "by_status": list(qs.values("status").annotate(count=Count("id"))),
            "by_criticality": list(qs.values("criticality").annotate(count=Count("id"))),
            "by_category": list(qs.values("category__name").annotate(count=Count("id"))),
        }
        return Response(data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class EnvironmentViewSet(viewsets.ModelViewSet):
    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer


class DeploymentViewSet(viewsets.ModelViewSet):
    queryset = Deployment.objects.select_related("application", "environment")
    serializer_class = DeploymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["application", "environment", "is_active"]


class LicenseViewSet(viewsets.ModelViewSet):
    queryset = License.objects.select_related("application")
    serializer_class = LicenseSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["application", "license_type"]
