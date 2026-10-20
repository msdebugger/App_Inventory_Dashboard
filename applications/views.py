from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum, Q
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from .filters import ApplicationFilter
from .forms import ApplicationForm, DeploymentForm, LicenseForm, ApplicationSearchForm
from .models import Application, AuditLogEntry, Category, Deployment, Environment, License, Vendor


class DashboardView(TemplateView):
    template_name = "applications/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        apps = Application.objects.all()

        ctx["total_apps"] = apps.count()
        ctx["total_annual_cost"] = apps.aggregate(total=Sum("annual_cost"))["total"] or 0
        ctx["critical_count"] = apps.filter(criticality=Application.Criticality.CRITICAL).count()
        ctx["active_count"] = apps.filter(status=Application.Status.ACTIVE).count()
        ctx["eol_soon_ids"] = [a.id for a in apps if a.is_end_of_life_soon]
        ctx["eol_soon_count"] = len(ctx["eol_soon_ids"])

        ctx["by_status"] = list(
            apps.values("status").annotate(count=Count("id")).order_by("-count")
        )
        ctx["by_criticality"] = list(
            apps.values("criticality").annotate(count=Count("id")).order_by("-count")
        )
        ctx["by_category"] = list(
            apps.values("category__name").annotate(count=Count("id")).order_by("-count")[:8]
        )
        ctx["by_hosting"] = list(
            apps.values("hosting_type").annotate(count=Count("id")).order_by("-count")
        )
        ctx["by_department"] = list(
            apps.exclude(department__isnull=True)
            .values("department__name")
            .annotate(count=Count("id"), total_cost=Sum("annual_cost"))
            .order_by("-total_cost")[:8]
        )

        ctx["top_cost_apps"] = apps.order_by("-annual_cost")[:5]
        ctx["recent_apps"] = apps.order_by("-created_at")[:6]
        ctx["vendor_count"] = Vendor.objects.count()
        ctx["department_count"] = apps.exclude(department__isnull=True).values("department").distinct().count()
        ctx["recent_audit"] = AuditLogEntry.objects.select_related("application", "actor")[:8]
        return ctx


class ApplicationListView(ListView):
    model = Application
    template_name = "applications/application_list.html"
    context_object_name = "applications"
    paginate_by = 12

    def get_queryset(self):
        qs = Application.objects.select_related("category", "vendor", "department").prefetch_related("tags")
        self.search_form = ApplicationSearchForm(self.request.GET or None)
        if self.search_form.is_valid() and self.search_form.cleaned_data.get("q"):
            q = self.search_form.cleaned_data["q"]
            qs = qs.filter(
                Q(name__icontains=q)
                | Q(description__icontains=q)
                | Q(owner_name__icontains=q)
                | Q(owner_email__icontains=q)
                | Q(vendor__name__icontains=q)
            )
        self.filterset = ApplicationFilter(self.request.GET or None, queryset=qs)
        return self.filterset.qs.order_by("name")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["filter"] = self.filterset
        ctx["search_form"] = self.search_form
        ctx["categories"] = Category.objects.all()
        querydict = self.request.GET.copy()
        querydict.pop("page", None)
        ctx["querystring"] = querydict.urlencode()
        return ctx


class ApplicationDetailView(DetailView):
    model = Application
    template_name = "applications/application_detail.html"
    context_object_name = "application"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Application.objects.select_related("category", "vendor", "department").prefetch_related(
            "tags", "deployments__environment", "licenses", "audit_entries__actor"
        )


class ApplicationCreateView(LoginRequiredMixin, CreateView):
    model = Application
    form_class = ApplicationForm
    template_name = "applications/application_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        AuditLogEntry.objects.create(
            application=self.object,
            application_name_snapshot=self.object.name,
            action=AuditLogEntry.Action.CREATED,
            actor=self.request.user if self.request.user.is_authenticated else None,
            notes="Created via web form",
        )
        messages.success(self.request, f'Application "{self.object.name}" created successfully.')
        return response


class ApplicationUpdateView(LoginRequiredMixin, UpdateView):
    model = Application
    form_class = ApplicationForm
    template_name = "applications/application_form.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def form_valid(self, form):
        response = super().form_valid(form)
        AuditLogEntry.objects.create(
            application=self.object,
            application_name_snapshot=self.object.name,
            action=AuditLogEntry.Action.UPDATED,
            actor=self.request.user if self.request.user.is_authenticated else None,
            notes="Updated via web form",
        )
        messages.success(self.request, f'Application "{self.object.name}" updated successfully.')
        return response


class ApplicationDeleteView(LoginRequiredMixin, DeleteView):
    model = Application
    template_name = "applications/application_confirm_delete.html"
    slug_field = "slug"
    slug_url_kwarg = "slug"
    success_url = reverse_lazy("application-list")

    def form_valid(self, form):
        name = self.object.name
        AuditLogEntry.objects.create(
            application=None,
            application_name_snapshot=name,
            action=AuditLogEntry.Action.DELETED,
            actor=self.request.user if self.request.user.is_authenticated else None,
            notes="Deleted via web form",
        )
        messages.success(self.request, f'Application "{name}" was deleted.')
        return super().form_valid(form)


class VendorListView(ListView):
    model = Vendor
    template_name = "applications/vendor_list.html"
    context_object_name = "vendors"
    paginate_by = 20

    def get_queryset(self):
        return Vendor.objects.annotate(app_count=Count("applications")).order_by("-app_count", "name")


class ReportsView(TemplateView):
    template_name = "applications/reports.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        apps = Application.objects.all()

        ctx["cost_by_category"] = list(
            apps.values("category__name").annotate(total=Sum("annual_cost"), count=Count("id")).order_by("-total")
        )
        ctx["expiring_licenses"] = License.objects.select_related("application").order_by("expiry_date")[:15]
        ctx["deployments_by_env"] = list(
            Deployment.objects.values("environment__name").annotate(count=Count("id")).order_by("-count")
        )
        ctx["eol_apps"] = [a for a in apps if a.is_end_of_life_soon]
        ctx["retired_apps"] = apps.filter(status=Application.Status.RETIRED)
        return ctx


@login_required
def add_deployment(request, slug):
    application = get_object_or_404(Application, slug=slug)
    if request.method == "POST":
        form = DeploymentForm(request.POST)
        if form.is_valid():
            deployment = form.save(commit=False)
            deployment.application = application
            deployment.save()
            messages.success(request, "Deployment added.")
            return redirect("application-detail", slug=slug)
    else:
        form = DeploymentForm(initial={"application": application})
    return render(request, "applications/simple_form.html", {
        "form": form, "title": f"Add Deployment - {application.name}", "application": application,
    })


@login_required
def add_license(request, slug):
    application = get_object_or_404(Application, slug=slug)
    if request.method == "POST":
        form = LicenseForm(request.POST)
        if form.is_valid():
            license_obj = form.save(commit=False)
            license_obj.application = application
            license_obj.save()
            messages.success(request, "License added.")
            return redirect("application-detail", slug=slug)
    else:
        form = LicenseForm(initial={"application": application})
    return render(request, "applications/simple_form.html", {
        "form": form, "title": f"Add License - {application.name}", "application": application,
    })
