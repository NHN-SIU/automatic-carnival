"""Forms for praksis_nhn_nautobot."""

from django import forms
from nautobot.apps.forms import NautobotBulkEditForm, NautobotFilterForm, NautobotModelForm, TagsBulkEditFormMixin

from praksis_nhn_nautobot import models


class NHNModelForm(NautobotModelForm):  # pylint: disable=too-many-ancestors
    """NHNModel creation/edit form."""

    class Meta:
        """Meta attributes."""

        model = models.NHNModel
        fields = [
            "name",
            "description",
        ]


class NHNModelBulkEditForm(TagsBulkEditFormMixin, NautobotBulkEditForm):  # pylint: disable=too-many-ancestors
    """NHNModel bulk edit form."""

    pk = forms.ModelMultipleChoiceField(queryset=models.NHNModel.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(required=False)

    class Meta:
        """Meta attributes."""

        nullable_fields = [
            "description",
        ]


class NHNModelFilterForm(NautobotFilterForm):
    """Filter form to filter searches."""

    model = models.NHNModel
    field_order = ["q", "name"]

    q = forms.CharField(
        required=False,
        label="Search",
        help_text="Search within Name or Slug.",
    )
    name = forms.CharField(required=False, label="Name")
