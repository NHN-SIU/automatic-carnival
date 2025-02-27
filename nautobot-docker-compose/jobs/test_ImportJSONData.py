from nautobot.apps.testing import run_job_for_testing, TransactionTestCase
from nautobot.extras.models import Job, JobLogEntry


class ImportJsonDataTestCase(TransactionTestCase):
    def set_up(self):
        job = Job.objects.get(job_class_name="ImportJSONData", module_name="my_job")
        job_result = run_job_for_testing(job)
        print("herhehehehehe")
    
    def test_check_tests(self):
        self.assertEqual(2, 2)