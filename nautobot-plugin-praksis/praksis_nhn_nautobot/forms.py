"""Forms for praksis_nhn_nautobot."""

from django import forms
from nautobot.apps.forms import NautobotBulkEditForm, NautobotFilterForm, NautobotModelForm, TagsBulkEditFormMixin

from praksis_nhn_nautobot import models


class SambandForm(NautobotModelForm):  # pylint: disable=too-many-ancestors
    """Samband creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = models.Samband
        fields = [
            "name",
            "description",
        ]


class SambandBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """Samband bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.Samband.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


class SambandFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    model = models.Samband
    field_order = ["q", "name"]

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Slug.",
    )
    name = forms.CharField(required=False, label="Name")
