from nautobot.apps import jobs



class MyNewJob(jobs.Job):
    class Meta:
        # metadata attributes go here
        name = "My New test Job" # Job name displayed in Nautobot UI - default is classs name
        description = "My new job description" # Displayed in Nautobot UI
        # approval_required    Default=False # Whether this Job requires approval from another userbefore it can be run 
        # dryrun_default¶    Default=False # Whether this Job should default to dry-run mode
        field_order = ["some_text_input"] # order input variables should be rendered
        # has_sensitive_variables   Default=True # when true: input parameters are not saved to the database
        # hidden  Default=False # Whether this Job should be hidden from the UI
        
    # input variable definitions go here
    some_text_input = jobs.StringVar(description="Some text input")
    # ... etc.

    def run(self, *, some_text_input):
        # code to execute when the Job is run goes here
        self.logger.info("some_text_input: %s", some_text_input)

from django.core.exceptions import FieldError
from django.db import transaction
from nautobot.dcim.models import Device, DeviceType, Location
from nautobot.extras.models import Status
#import json
name = "Import json to nautobot Jobs"  # optional, but recommended to define a grouping name
import json
"""
Sources:
 - atomic jobs: https://josh-v.com/nautobot-atomic-jobs/

"""

# Get the "active" object
status_active = Status.objects.get(name="Active")

class ImportJSONData(jobs.Job):

    class Meta:
        name = "Import JSON Data"
        description = "Import JSON data into Nautobot"

    json_file = jobs.FileVar(required = False, description="Upoad JSON file containing the data")

    def load_json_file(self, json_file):
        """ 
        Reads and loads JSON data from a file-like object.

        Parameters:
            json_file: A file-like object opened in binary mode.

        Logs:
            - Error if the file is empty.
            - Error if decoding fails.
            - Error if JSON parsing fails.
            - Info if JSON is successfully loaded.
        """
        try:
            data_byte = json_file.read()
            if not data_byte:
                self.logger.error("The uploaded JSON file is empty.")
                return None  # Explicitly return None when file is empty

            json_string = data_byte.decode("utf-8")  # Handle potential decoding errors
            data = json.loads(json_string)  # Handle potential JSON errors
            self.logger.info(f"Successfully loaded JSON data, type: %s", type(json_file))
            return data  # Return the parsed JSON data
        
        except UnicodeDecodeError as e:
            self.logger.error("Failed to decode JSON file: %s", str(e))
        except json.JSONDecodeError as e:
            self.logger.error("Invalid JSON format: %s", str(e))
        except:
            return None


    @transaction.atomic
    def run(self, *, json_file):
        self.logger.info("printing data input: %s", json_file)
        # Load json data
        if json_file == None:
            try:
                self.logger.info("No file sent. Read from local data.")
                data = self.load_json("test-data.json")
            except:
                raise Exception("No file sent and no file found in local storage")
        else:
            data = self.load_json_file(json_file)
        

        self.process_data(data)
        return "yeyeyeye it runs!"

    def process_data(self, json_data):
        
        #Process the JSON data and create/update Nautobot objects.
        
        # Example: Create devices from JSON data
        for item in json_data:
            device_name = item["name"]
            device_type_name = item["type"]
            location_name = item["location"]
            self.logger.info("name: %s -- type: %s -- location: %s", device_name, device_type_name, location_name)
        """
        Create Objects: 
            - Use Django's ORM to create and save instances of the necessary models with the data from your JSON file.
            - Ensure that you handle any dependencies or related objects appropriately.
        """
        """
        Circuit required fields
         - Circuit ID - A unique identifier for the circuit (must be unique per provider)
            This is usually an ID or number given by the provider.
Provider – The service provider that delivers the circuit (ForeignKey to a Provider object)​
DOCS.NAUTOBOT.COM
. Every circuit must be associated with a provider, and the combination of provider + circuit ID must be unique​
DOCS.NAUTOBOT.COM
.
Circuit Type – A user-defined type/classification for the circuit (ForeignKey to a CircuitType)​
DOCS.NAUTOBOT.COM
. This describes the kind of service (e.g. Internet, MPLS, backhaul) and must be created in advance.
Status – The operational status of the circuit (ForeignKey to a Status object). Each circuit must be assigned a status (e.g. Planned, Active, Decommissioned, etc.)​
DOCS.NAUTOBOT.COM
​
DOCS.NAUTOBOT.COM
 to indicate its state in its lifecycle.
(Other Fields) – Circuits have additional optional fields such as description, install_date (installation date), and commit_rate (bandwidth)​
DOCS.NAUTOBOT.COM
, and may be associated with a Tenant (to denote customer or internal tenant ownership)​
DOCS.NAUTOBOT.COM
. These are not required for basic import but can be included if relevant.
        """
        #     # Retrieve or create the DeviceType
        #     device_type, created = DeviceType.objects.get_or_create(
        #         model=device_type_name,
        #         defaults={"manufacturer": None},  # Set appropriate manufacturer
        #     )
        #     if created:
        #         self.log_info(f"Created new DeviceType: {device_type_name}")

        #     # Retrieve or create the Location
        #     location, created = Location.objects.get_or_create(name=location_name)
        #     if created:
        #         self.log_info(f"Created new Location: {location_name}")

        #     # Create or update the Device
        #     device, created = Device.objects.update_or_create(
        #         name=device_name,
        #         defaults={
        #             "device_type": device_type,
        #             "location": location,
        #             # Add other fields as necessary
        #         },
        #     )
        #     if created:
        #         self.log_info(f"Created new Device: {device_name}")
        #     else:
        #         self.log_info(f"Updated existing Device: {device_name}")



jobs.register_jobs(MyNewJob, ImportJSONData)