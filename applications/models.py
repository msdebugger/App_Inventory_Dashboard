import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class TimeStampedModel(models.Model):
    """Abstract base providing created/updated bookkeeping."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Department(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text="Short department code, e.g. FIN, HR, ENG")
    cost_center = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Vendor(TimeStampedModel):
    name = models.CharField(max_length=200, unique=True)
    website = models.URLField(blank=True)
    support_email = models.EmailField(blank=True)
    support_phone = models.CharField(max_length=30, blank=True)
    account_manager = models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def application_count(self):
        return self.applications.count()


class Category(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=50,
        blank=True,
        default="bi-box",
        help_text="Bootstrap icon class, e.g. bi-cloud, bi-database",
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Tag(TimeStampedModel):
    name = models.CharField(max_length=60, unique=True)
    color = models.CharField(max_length=20, default="secondary", help_text="Bootstrap color, e.g. success, danger")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Environment(TimeStampedModel):
    """A deployment tier, e.g. Production, Staging, QA, Development."""

    class EnvType(models.TextChoices):
        PRODUCTION = "PROD", "Production"
        STAGING = "STAGE", "Staging"
        QA = "QA", "QA / Test"
        DEVELOPMENT = "DEV", "Development"
        DR = "DR", "Disaster Recovery"

    name = models.CharField(max_length=10, choices=EnvType.choices, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.get_name_display()


class Application(TimeStampedModel):
    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Planned"
        ACTIVE = "ACTIVE", "Active"
        DEPRECATED = "DEPRECATED", "Deprecated"
        RETIRED = "RETIRED", "Retired"
        MAINTENANCE = "MAINTENANCE", "Under Maintenance"

    class Criticality(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        CRITICAL = "CRITICAL", "Critical"

    class AppType(models.TextChoices):
        WEB = "WEB", "Web Application"
        DESKTOP = "DESKTOP", "Desktop Application"
        MOBILE = "MOBILE", "Mobile Application"
        API = "API", "API / Microservice"
        BATCH = "BATCH", "Batch / Scheduled Job"
        DATABASE = "DATABASE", "Database System"

    class HostingType(models.TextChoices):
        CLOUD = "CLOUD", "Public Cloud"
        ON_PREM = "ON_PREM", "On-Premises"
        HYBRID = "HYBRID", "Hybrid"
        SAAS = "SAAS", "SaaS (Vendor Hosted)"

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)

    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="applications"
    )
    vendor = models.ForeignKey(
        Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name="applications"
    )
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="applications"
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="applications")

    owner_name = models.CharField(max_length=150, blank=True, help_text="Business/application owner")
    owner_email = models.EmailField(blank=True)
    technical_contact = models.CharField(max_length=150, blank=True)
    technical_contact_email = models.EmailField(blank=True)

    version = models.CharField(max_length=50, blank=True)
    application_type = models.CharField(max_length=20, choices=AppType.choices, default=AppType.WEB)
    hosting_type = models.CharField(max_length=20, choices=HostingType.choices, default=HostingType.CLOUD)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    criticality = models.CharField(max_length=20, choices=Criticality.choices, default=Criticality.MEDIUM)

    url = models.URLField(blank=True)
    repository_url = models.URLField(blank=True)

    launch_date = models.DateField(null=True, blank=True)
    end_of_life_date = models.DateField(null=True, blank=True)
    last_audit_date = models.DateField(null=True, blank=True)

    annual_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=0,
        validators=[MinValueValidator(0)],
        help_text="Total annual cost including license + support",
    )

    uptime_sla = models.DecimalField(
        max_digits=5, decimal_places=2, default=99.0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Committed SLA uptime percentage",
    )

    is_business_critical = models.BooleanField(default=False)
    data_classification = models.CharField(
        max_length=20,
        choices=[
            ("PUBLIC", "Public"),
            ("INTERNAL", "Internal"),
            ("CONFIDENTIAL", "Confidential"),
            ("RESTRICTED", "Restricted"),
        ],
        default="INTERNAL",
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["criticality"]),
            models.Index(fields=["application_type"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Application.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("application-detail", kwargs={"slug": self.slug})

    @property
    def is_end_of_life_soon(self):
        if not self.end_of_life_date:
            return False
        return (self.end_of_life_date - timezone.now().date()).days <= 180

    @property
    def deployment_count(self):
        return self.deployments.count()

    @property
    def active_license_count(self):
        return self.licenses.filter(expiry_date__gte=timezone.now().date()).count()


class Deployment(TimeStampedModel):
    """Represents an application deployed into a specific environment/server."""

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="deployments")
    environment = models.ForeignKey(Environment, on_delete=models.CASCADE, related_name="deployments")
    server_name = models.CharField(max_length=150)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    operating_system = models.CharField(max_length=100, blank=True)
    cpu_cores = models.PositiveIntegerField(null=True, blank=True)
    ram_gb = models.PositiveIntegerField(null=True, blank=True)
    storage_gb = models.PositiveIntegerField(null=True, blank=True)
    region = models.CharField(max_length=100, blank=True, help_text="e.g. us-east-1, ap-south-1")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["application__name", "environment__name"]
        unique_together = ("application", "environment", "server_name")

    def __str__(self):
        return f"{self.application.name} - {self.environment} ({self.server_name})"


class License(TimeStampedModel):
    class LicenseType(models.TextChoices):
        PERPETUAL = "PERPETUAL", "Perpetual"
        SUBSCRIPTION = "SUBSCRIPTION", "Subscription"
        OPEN_SOURCE = "OPEN_SOURCE", "Open Source"
        FREEMIUM = "FREEMIUM", "Freemium"
        TRIAL = "TRIAL", "Trial"

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="licenses")
    license_type = models.CharField(max_length=20, choices=LicenseType.choices, default=LicenseType.SUBSCRIPTION)
    license_key = models.CharField(max_length=200, blank=True)
    seats_purchased = models.PositiveIntegerField(default=1)
    seats_used = models.PositiveIntegerField(default=0)
    purchase_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ["-expiry_date"]

    def __str__(self):
        return f"{self.application.name} license ({self.get_license_type_display()})"

    @property
    def is_expired(self):
        if not self.expiry_date:
            return False
        return self.expiry_date < timezone.now().date()

    @property
    def seats_available(self):
        return max(self.seats_purchased - self.seats_used, 0)


class AuditLogEntry(TimeStampedModel):
    """Lightweight change log for compliance / governance tracking."""

    class Action(models.TextChoices):
        CREATED = "CREATED", "Created"
        UPDATED = "UPDATED", "Updated"
        DELETED = "DELETED", "Deleted"
        REVIEWED = "REVIEWED", "Reviewed"

    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name="audit_entries", null=True, blank=True
    )
    application_name_snapshot = models.CharField(max_length=200, blank=True)
    action = models.CharField(max_length=20, choices=Action.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Audit log entries"

    def __str__(self):
        return f"{self.get_action_display()} - {self.application_name_snapshot or self.application}"
