from django.urls import path

from . import views

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
    path("applications/", views.ApplicationListView.as_view(), name="application-list"),
    path("applications/add/", views.ApplicationCreateView.as_view(), name="application-add"),
    path("applications/<slug:slug>/", views.ApplicationDetailView.as_view(), name="application-detail"),
    path("applications/<slug:slug>/edit/", views.ApplicationUpdateView.as_view(), name="application-edit"),
    path("applications/<slug:slug>/delete/", views.ApplicationDeleteView.as_view(), name="application-delete"),
    path("applications/<slug:slug>/deployments/add/", views.add_deployment, name="deployment-add"),
    path("applications/<slug:slug>/licenses/add/", views.add_license, name="license-add"),
    path("vendors/", views.VendorListView.as_view(), name="vendor-list"),
    path("reports/", views.ReportsView.as_view(), name="reports"),
]
