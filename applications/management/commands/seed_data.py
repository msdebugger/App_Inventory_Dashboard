import random
from datetime import timedelta, date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from applications.models import (
    Application, AuditLogEntry, Category, Department, Deployment,
    Environment, License, Tag, Vendor,
)

CATEGORIES = [
    ("ERP", "bi-boxes", "Enterprise resource planning systems"),
    ("CRM", "bi-people-fill", "Customer relationship management"),
    ("HR & Payroll", "bi-person-badge", "Human resources and payroll systems"),
    ("Collaboration", "bi-chat-dots-fill", "Team communication and collaboration tools"),
    ("Finance & Accounting", "bi-calculator-fill", "Financial management systems"),
    ("DevOps & CI/CD", "bi-tools", "Development and deployment tooling"),
    ("Security", "bi-shield-lock-fill", "Security and identity tools"),
    ("Data & Analytics", "bi-graph-up-arrow", "BI, analytics, and data platforms"),
    ("Customer Support", "bi-headset", "Helpdesk and support ticketing"),
    ("Marketing", "bi-megaphone-fill", "Marketing automation and campaign tools"),
    ("Infrastructure", "bi-hdd-rack-fill", "Core infrastructure and platform services"),
    ("E-Commerce", "bi-cart-fill", "Online storefront and order management"),
]

DEPARTMENTS = [
    ("Information Technology", "IT", "CC-1000"),
    ("Human Resources", "HR", "CC-2000"),
    ("Finance", "FIN", "CC-3000"),
    ("Sales", "SALES", "CC-4000"),
    ("Marketing", "MKT", "CC-5000"),
    ("Customer Success", "CS", "CC-6000"),
    ("Engineering", "ENG", "CC-7000"),
    ("Operations", "OPS", "CC-8000"),
]

VENDORS = [
    ("Salesforce Inc.", "salesforce.com", "support@salesforce.com", "Priya Nair"),
    ("Microsoft Corporation", "microsoft.com", "support@microsoft.com", "James Carter"),
    ("Atlassian", "atlassian.com", "support@atlassian.com", "Wei Zhang"),
    ("SAP SE", "sap.com", "support@sap.com", "Hannah Fischer"),
    ("Oracle Corporation", "oracle.com", "support@oracle.com", "Robert Alvarez"),
    ("ServiceNow", "servicenow.com", "support@servicenow.com", "Meera Iyer"),
    ("Workday Inc.", "workday.com", "support@workday.com", "Daniel Kim"),
    ("GitHub (Microsoft)", "github.com", "support@github.com", "Sofia Rossi"),
    ("GitLab Inc.", "gitlab.com", "support@gitlab.com", "Tom Becker"),
    ("Slack Technologies", "slack.com", "support@slack.com", "Aisha Rahman"),
    ("Zendesk", "zendesk.com", "support@zendesk.com", "Lucas Meyer"),
    ("HubSpot", "hubspot.com", "support@hubspot.com", "Emily Chen"),
    ("Amazon Web Services", "aws.amazon.com", "aws-support@amazon.com", "Michael Ortiz"),
    ("Snowflake Inc.", "snowflake.com", "support@snowflake.com", "Grace Park"),
    ("Okta Inc.", "okta.com", "support@okta.com", "Nathan Brooks"),
    ("Adobe Inc.", "adobe.com", "support@adobe.com", "Isabella Moreau"),
    ("Zoom Video Communications", "zoom.us", "support@zoom.us", "Kevin O'Neil"),
    ("Docker Inc.", "docker.com", "support@docker.com", "Anya Petrova"),
    ("Internal Development", "", "", ""),
    ("Shopify Inc.", "shopify.com", "support@shopify.com", "Ben Whitfield"),
]

TAGS = [
    ("PCI-DSS", "danger"), ("GDPR", "primary"), ("SOC2", "success"),
    ("HIPAA", "warning"), ("Legacy", "secondary"), ("Cloud-Native", "info"),
    ("Mission-Critical", "danger"), ("Open-Source", "success"), ("AI/ML", "primary"),
    ("Customer-Facing", "info"), ("Internal-Only", "secondary"), ("Multi-Tenant", "primary"),
]

APP_TEMPLATES = [
    ("Salesforce Sales Cloud", "CRM", "Salesforce Inc.", "Sales", Application.AppType.WEB, Application.HostingType.SAAS, Application.Criticality.CRITICAL, "Core CRM platform used by the global sales organization to manage leads, opportunities, and forecasts."),
    ("Microsoft 365", "Collaboration", "Microsoft Corporation", "Information Technology", Application.AppType.WEB, Application.HostingType.SAAS, Application.Criticality.CRITICAL, "Company-wide productivity suite including Outlook, Teams, SharePoint, and OneDrive."),
    ("SAP S/4HANA", "ERP", "SAP SE", "Finance", Application.AppType.WEB, Application.HostingType.HYBRID, Application.Criticality.CRITICAL, "Core enterprise resource planning system handling procurement, inventory, and financial consolidation."),
    ("Workday HCM", "HR & Payroll", "Workday Inc.", "Human Resources", Application.AppType.WEB, Application.HostingType.SAAS, Application.Criticality.HIGH, "Human capital management platform for payroll, benefits, and talent management."),
    ("Jira Software", "DevOps & CI/CD", "Atlassian", "Engineering", Application.AppType.WEB, Application.HostingType.SAAS, Application.Criticality.HIGH, "Agile project tracking and issue management for all engineering teams."),
    ("Confluence", "Collaboration", "Atlassian", "Engineering", Application.AppType.WEB, Application.HostingType.SAAS, Application.Criticality.MEDIUM, "Team wiki and knowledge base for documentation and specs."),
    ("GitHub Enterprise", "DevOps & CI/CD", "GitHub (Microsoft)", "Engineering", Application.AppType.WEB, Application.HostingType.SAAS, Application.Criticality.CRITICAL, "Source control and CI/CD pipelines for all engineering repositories."),
    ("GitLab CI", "DevOps & CI/CD", "GitLab Inc.", "Engineering", Application.AppType.WEB, Application.HostingType.CLOUD, Application.Criticality.HIGH, "Secondary CI/CD platform used for infrastructure automation pipelines."),
    ("ServiceNow ITSM", "Customer Support", "ServiceNow", "Information Technology", Application.AppType.WEB, Application.HostingType.SAAS, Application.Criticality.HIGH, "IT service management platform handling incidents, changes, and problem tickets."),
    ("Zendesk Support", "Customer Support", "Zendesk", "Customer Success", Application.AppType.WEB, Application.HostingType.SAAS, Application.Criticality.HIGH, "Customer support ticketing and knowledge base."),
    ("HubSpot Marketing Hub", "Marketing", "HubSpot", "Marketing", Application.AppType.WEB, Application.HostingType.SAAS, Application.Criticality.MEDIUM, "Marketing automation, email campaigns, and lead nurturing."),
    ("Snowflake Data Warehouse", "Data & Analytics", "Snowflake Inc.", "Engineering", Application.AppType.DATABASE, Application.HostingType.CLOUD, Application.Criticality.CRITICAL, "Central cloud data warehouse powering analytics and BI dashboards."),
    ("Okta Identity Cloud", "Security", "Okta Inc.", "Information Technology", Application.AppType.WEB, Application.HostingType.SAAS, Application.Criticality.CRITICAL, "Single sign-on and identity management for all internal and SaaS applications."),
    ("Adobe Creative Cloud", "Marketing", "Adobe Inc.", "Marketing", Application.AppType.DESKTOP, Application.HostingType.HYBRID, Application.Criticality.LOW, "Design and creative suite for the marketing/brand team."),
    ("Zoom", "Collaboration", "Zoom Video Communications", "Information Technology", Application.AppType.WEB, Application.HostingType.SAAS, Application.Criticality.HIGH, "Video conferencing platform used company-wide."),
    ("Internal Payments Gateway", "Finance & Accounting", "Internal Development", "Engineering", Application.AppType.API, Application.HostingType.CLOUD, Application.Criticality.CRITICAL, "In-house microservice handling payment processing and settlement."),
    ("Customer Portal", "E-Commerce", "Internal Development", "Engineering", Application.AppType.WEB, Application.HostingType.CLOUD, Application.Criticality.CRITICAL, "Customer-facing self-service portal for account management and billing."),
    ("Inventory Sync Service", "Infrastructure", "Internal Development", "Operations", Application.AppType.BATCH, Application.HostingType.ON_PREM, Application.Criticality.MEDIUM, "Nightly batch job that reconciles warehouse stock levels across regions."),
    ("Legacy Billing System", "Finance & Accounting", "Oracle Corporation", "Finance", Application.AppType.DESKTOP, Application.HostingType.ON_PREM, Application.Criticality.MEDIUM, "Legacy on-premise billing engine slated for replacement."),
    ("Docker Registry", "DevOps & CI/CD", "Docker Inc.", "Engineering", Application.AppType.API, Application.HostingType.ON_PREM, Application.Criticality.MEDIUM, "Internal container image registry for microservices."),
    ("Shopify Storefront", "E-Commerce", "Shopify Inc.", "Sales", Application.AppType.WEB, Application.HostingType.SAAS, Application.Criticality.HIGH, "Public e-commerce storefront for direct-to-consumer sales."),
    ("Slack", "Collaboration", "Slack Technologies", "Information Technology", Application.AppType.WEB, Application.HostingType.SAAS, Application.Criticality.HIGH, "Company-wide instant messaging and channel-based collaboration."),
    ("AWS CloudWatch Dashboard", "Infrastructure", "Amazon Web Services", "Operations", Application.AppType.WEB, Application.HostingType.CLOUD, Application.Criticality.MEDIUM, "Centralized monitoring and alerting dashboard for cloud infrastructure."),
    ("Employee Onboarding Portal", "HR & Payroll", "Internal Development", "Human Resources", Application.AppType.WEB, Application.HostingType.CLOUD, Application.Criticality.LOW, "Internal tool guiding new hires through onboarding checklists."),
    ("Fraud Detection Engine", "Security", "Internal Development", "Engineering", Application.AppType.API, Application.HostingType.CLOUD, Application.Criticality.CRITICAL, "Real-time ML-based fraud scoring service for transactions."),
    ("Legacy HR Timesheet System", "HR & Payroll", "Internal Development", "Human Resources", Application.AppType.DESKTOP, Application.HostingType.ON_PREM, Application.Criticality.LOW, "Deprecated desktop timesheet application awaiting decommission."),
    ("Data Pipeline Orchestrator", "Data & Analytics", "Internal Development", "Engineering", Application.AppType.BATCH, Application.HostingType.CLOUD, Application.Criticality.HIGH, "Airflow-based orchestration for ETL pipelines feeding the data warehouse."),
    ("Vendor Risk Assessment Tool", "Security", "Internal Development", "Information Technology", Application.AppType.WEB, Application.HostingType.ON_PREM, Application.Criticality.MEDIUM, "Internal tool for tracking third-party vendor security assessments."),
    ("Mobile Banking App", "E-Commerce", "Internal Development", "Engineering", Application.AppType.MOBILE, Application.HostingType.CLOUD, Application.Criticality.CRITICAL, "Customer-facing iOS/Android application for account management and transfers."),
    ("Expense Reporting Tool", "Finance & Accounting", "SAP SE", "Finance", Application.AppType.WEB, Application.HostingType.SAAS, Application.Criticality.MEDIUM, "Employee expense submission and reimbursement workflow."),
]

FIRST_NAMES = ["Alex","Jordan","Taylor","Morgan","Casey","Riley","Sam","Jamie","Priya","Wei","Amir","Sofia","Liam","Noah","Emma","Olivia","Ava","Ethan","Mia","Lucas"]
LAST_NAMES = ["Johnson","Smith","Patel","Kim","Garcia","Chen","Muller","Brown","Davis","Wilson","Anderson","Taylor","Moore","Martin","Lee","Clark","Walker","Young","King","Wright"]


class Command(BaseCommand):
    help = "Seed the database with realistic dummy application inventory data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush", action="store_true", help="Delete existing inventory data before seeding."
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Flushing existing inventory data...")
            Deployment.objects.all().delete()
            License.objects.all().delete()
            AuditLogEntry.objects.all().delete()
            Application.objects.all().delete()
            Vendor.objects.all().delete()
            Category.objects.all().delete()
            Department.objects.all().delete()
            Tag.objects.all().delete()
            Environment.objects.all().delete()

        random.seed(42)

        self.stdout.write("Creating environments...")
        environments = {}
        for env_code, _ in Environment.EnvType.choices:
            env, _ = Environment.objects.get_or_create(name=env_code)
            environments[env_code] = env

        self.stdout.write("Creating categories...")
        categories = {}
        for name, icon, desc in CATEGORIES:
            cat, _ = Category.objects.get_or_create(name=name, defaults={"icon": icon, "description": desc})
            categories[name] = cat

        self.stdout.write("Creating departments...")
        departments = {}
        for name, code, cc in DEPARTMENTS:
            dept, _ = Department.objects.get_or_create(name=name, defaults={"code": code, "cost_center": cc})
            departments[name] = dept

        self.stdout.write("Creating vendors...")
        vendors = {}
        for name, domain, email, manager in VENDORS:
            website = f"https://www.{domain}" if domain else ""
            vendor, _ = Vendor.objects.get_or_create(
                name=name,
                defaults={
                    "website": website,
                    "support_email": email,
                    "support_phone": f"+1-800-{random.randint(100,999)}-{random.randint(1000,9999)}" if domain else "",
                    "account_manager": manager,
                },
            )
            vendors[name] = vendor

        self.stdout.write("Creating tags...")
        tags = {}
        for name, color in TAGS:
            tag, _ = Tag.objects.get_or_create(name=name, defaults={"color": color})
            tags[name] = tag

        self.stdout.write("Creating applications...")
        today = timezone.now().date()
        created_apps = []

        for (name, cat_name, vendor_name, dept_name, app_type, hosting, criticality, description) in APP_TEMPLATES:
            status_choices = [Application.Status.ACTIVE] * 6 + [
                Application.Status.MAINTENANCE, Application.Status.DEPRECATED,
                Application.Status.PLANNED, Application.Status.RETIRED,
            ]
            status = random.choice(status_choices)
            launch_date = today - timedelta(days=random.randint(180, 2500))
            eol_date = None
            if status in (Application.Status.DEPRECATED, Application.Status.RETIRED) or random.random() < 0.25:
                eol_date = today + timedelta(days=random.randint(-90, 400))

            owner_first, owner_last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
            tech_first, tech_last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)

            app = Application.objects.create(
                name=name,
                description=description,
                category=categories[cat_name],
                vendor=vendors[vendor_name],
                department=departments[dept_name],
                owner_name=f"{owner_first} {owner_last}",
                owner_email=f"{owner_first.lower()}.{owner_last.lower()}@company.com",
                technical_contact=f"{tech_first} {tech_last}",
                technical_contact_email=f"{tech_first.lower()}.{tech_last.lower()}@company.com",
                version=f"{random.randint(1,9)}.{random.randint(0,20)}.{random.randint(0,9)}",
                application_type=app_type,
                hosting_type=hosting,
                status=status,
                criticality=criticality,
                url=f"https://{name.lower().replace(' ', '-').replace('/', '-')}.company.com" if random.random() < 0.6 else "",
                repository_url=f"https://github.com/company/{name.lower().replace(' ', '-')}" if vendor_name == "Internal Development" else "",
                launch_date=launch_date,
                end_of_life_date=eol_date,
                last_audit_date=today - timedelta(days=random.randint(10, 365)),
                annual_cost=round(random.uniform(1500, 250000), 2),
                uptime_sla=round(random.uniform(97.0, 99.99), 2),
                is_business_critical=criticality in (Application.Criticality.CRITICAL, Application.Criticality.HIGH),
                data_classification=random.choice(["PUBLIC", "INTERNAL", "CONFIDENTIAL", "RESTRICTED"]),
            )

            app_tags = random.sample(list(tags.values()), k=random.randint(1, 4))
            app.tags.set(app_tags)

            num_envs = random.randint(1, 4)
            chosen_envs = random.sample(list(environments.values()), k=num_envs)
            for env in chosen_envs:
                Deployment.objects.create(
                    application=app,
                    environment=env,
                    server_name=f"{name.split()[0].lower()}-{env.name.lower()}-{random.randint(1,9):02d}",
                    ip_address=f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
                    operating_system=random.choice(["Ubuntu 22.04", "RHEL 9", "Windows Server 2022", "Amazon Linux 2023", "Debian 12"]),
                    cpu_cores=random.choice([2, 4, 8, 16, 32]),
                    ram_gb=random.choice([4, 8, 16, 32, 64, 128]),
                    storage_gb=random.choice([50, 100, 250, 500, 1000]),
                    region=random.choice(["us-east-1", "us-west-2", "eu-west-1", "ap-south-1", "on-prem-dc1"]),
                    is_active=status == Application.Status.ACTIVE,
                )

            if random.random() < 0.8:
                seats_purchased = random.randint(5, 500)
                License.objects.create(
                    application=app,
                    license_type=random.choice(License.LicenseType.values),
                    license_key=f"LIC-{random.randint(100000,999999)}-{random.randint(1000,9999)}",
                    seats_purchased=seats_purchased,
                    seats_used=random.randint(0, seats_purchased),
                    purchase_date=launch_date,
                    expiry_date=today + timedelta(days=random.randint(-60, 500)),
                    cost=round(random.uniform(500, 80000), 2),
                )

            AuditLogEntry.objects.create(
                application=app,
                application_name_snapshot=app.name,
                action=AuditLogEntry.Action.CREATED,
                notes="Seeded via initial data load.",
            )

            created_apps.append(app)

        self.stdout.write(self.style.SUCCESS(
            f"\nSeed complete!\n"
            f"  Categories:   {Category.objects.count()}\n"
            f"  Departments:  {Department.objects.count()}\n"
            f"  Vendors:      {Vendor.objects.count()}\n"
            f"  Tags:         {Tag.objects.count()}\n"
            f"  Environments: {Environment.objects.count()}\n"
            f"  Applications: {Application.objects.count()}\n"
            f"  Deployments:  {Deployment.objects.count()}\n"
            f"  Licenses:     {License.objects.count()}\n"
            f"\nCreate an account with `python manage.py createsuperuser` before signing in.\n"
        ))
