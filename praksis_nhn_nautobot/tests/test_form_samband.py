"""Test samband forms."""

from django.test import TestCase

from praksis_nhn_nautobot import forms


class SambandTest(TestCase):
    """Test Samband forms."""

    def test_specifying_all_fields_success(self):
        form = forms.SambandForm(
            data={
                "name": "Development",
                "description": "Development Testing",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_specifying_only_required_success(self):
        form = forms.SambandForm(
            data={
                "name": "Development",
            }
        )
        self.assertTrue(form.is_valid())
        self.assertTrue(form.save())

    def test_validate_name_samband_is_required(self):
        form = forms.SambandForm(data={"description": "Development Testing"})
        self.assertFalse(form.is_valid())
        self.assertIn("This field is required.", form.errors["name"])
