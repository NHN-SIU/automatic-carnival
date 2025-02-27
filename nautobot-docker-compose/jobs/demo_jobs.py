"""
Demo job for inspiration taken from:
https://josh-v.com/nautobot-atomic-jobs/

"""

"""Demonstration of Jobs."""
from django.core.exceptions import FieldError
from django.db import transaction

from nautobot.apps.jobs import Job
from nautobot.dcim.models import LocationType, Location
from nautobot.extras.models import Status

name = "Sandbox Jobs"

status_active = Status.objects.get(name="Active")

class CreateSites(Job):
    """Create Sites Job."""

    class Meta:
        """Meta Class."""

        name = "Create Sites"
        description = "Create Defined Sites"
        commit_default = False

    @transaction.atomic
    def run(self):
        """Run Method."""
        # Perform the work of the job
        # Create location types
        location_types = [
            {"name": "Datacenter"},
            {"name": "Office"},
            {"name": "Remote"},
        ]

        location_type_objects = {}
        for location_type in location_types:
            self.logger.info(f"Creating location type {location_type['name']}")
            location_type_obj, _created = LocationType.objects.get_or_create(**location_type)
            if _created:
                self.logger.info("Created location type %s", location_type_obj)
            else:
                self.logger.info("Location type %s already exists", location_type_obj)
            location_type_obj.validated_save()

            # Add to the location_type_objects dictionary with the name as the key
            location_type_objects[location_type["name"]] = location_type_obj

        # Create sites
        sites = [
            {"name": "Datacenter 1", "location_type": "Datacenter"},
            {"name": "Office 1", "location_type": "Office"},
            # This has some bad data, slug is no longer part of the system
            {"name": "Remote 1", "slug": "remote_1", "location_type": "Remote"},
        ]

        for site in sites:
            self.logger.info(f"Creating site {site['name']}")
            site_dictionary = {
                "name": site["name"],
                "location_type": location_type_objects[site["location_type"]],
                "status": status_active,
            }
            if site.get("slug"):
                site_dictionary["slug"] = site["slug"]

            try:
                site_obj, _created = Location.objects.get_or_create(**site_dictionary)

                if _created:
                    self.logger.info("Created site %s", site_obj)
                else:
                    self.logger.info("Site %s already exists", site_obj)
                site_obj.validated_save()
            except FieldError:
                self.logger.error(f"Failed to create site {site['name']}")
                raise FieldError(f"Failed to create site {site['name']}")