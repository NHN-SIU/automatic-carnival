"""Test nhnmodel forms."""

from django.test import TestCase

from praksis_nhn_nautobot import forms


class NHNModelTest(TestCase):
    """Test NHNModel forms."""

    def test_specifying_all_fields_success(self):
        form = forms.NHNModelForm(
            data={
                "name": "Development",
                "description": "Development Testing",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_specifying_only_required_success(self):
        form = forms.NHNModelForm(
            data={
                "name": "Development",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_validate_name_nhnmodel_is_required(self):
        form = forms.NHNModelForm(data={"description": "Development Testing"})
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors["name"])
