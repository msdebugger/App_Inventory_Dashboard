from rest_framework.routers import DefaultRouter

from . import api_views

router = DefaultRouter()
router.register(r"applications", api_views.ApplicationViewSet, basename="api-application")
router.register(r"categories", api_views.CategoryViewSet, basename="api-category")
router.register(r"vendors", api_views.VendorViewSet, basename="api-vendor")
router.register(r"departments", api_views.DepartmentViewSet, basename="api-department")
router.register(r"tags", api_views.TagViewSet, basename="api-tag")
router.register(r"environments", api_views.EnvironmentViewSet, basename="api-environment")
router.register(r"deployments", api_views.DeploymentViewSet, basename="api-deployment")
router.register(r"licenses", api_views.LicenseViewSet, basename="api-license")

urlpatterns = router.urls
