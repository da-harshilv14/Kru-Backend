from django import forms
from loginSignup.models import User

class BroadcastForm(forms.Form):

    TARGET_CHOICES = [
        ("all", "All Users"),
        ("farmer", "Farmers"),
        ("officer", "Officers"),
        ("subsidy_provider", "Subsidy Providers"),
        ("admin", "Admins"),
        ("custom", "Custom Users"),
    ]

    target_group = forms.ChoiceField(choices=TARGET_CHOICES)
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        help_text="Only used when target_group = Custom"
    )

    subject = forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea)
