from .models import Application


def inventory_stats(request):
    """Expose lightweight sitewide counts to every template (used in navbar badge)."""
    if not request.path.startswith("/admin"):
        return {
            "nav_total_apps": Application.objects.count(),
            "nav_critical_apps": Application.objects.filter(
                criticality=Application.Criticality.CRITICAL
            ).count(),
        }
    return {}
