from django import forms

from .models import Application, Deployment, License


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        exclude = ["uuid", "slug", "created_at", "updated_at"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "launch_date": forms.DateInput(attrs={"type": "date"}),
            "end_of_life_date": forms.DateInput(attrs={"type": "date"}),
            "last_audit_date": forms.DateInput(attrs={"type": "date"}),
            "tags": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxSelectMultiple):
                continue


class DeploymentForm(forms.ModelForm):
    class Meta:
        model = Deployment
        exclude = ["created_at", "updated_at"]


class LicenseForm(forms.ModelForm):
    class Meta:
        model = License
        exclude = ["created_at", "updated_at"]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
        }


class ApplicationSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(attrs={
            "class": (
                "w-full rounded-lg border border-slate-300 dark:border-slate-600 "
                "bg-white dark:bg-[#1c2233] text-navy-700 dark:text-slate-100 text-sm "
                "px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-accent-500"
            ),
            "placeholder": "Search applications by name, owner, description...",
        }),
    )
