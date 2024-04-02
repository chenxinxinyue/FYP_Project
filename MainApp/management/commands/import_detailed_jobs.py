from django.core.management.base import BaseCommand
from MainApp.models import DetailedJob
import csv


class Command(BaseCommand):
    help = 'Import jobs from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The CSV file to import.')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']
        with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                try:
                    med_salary = None if not row['med_salary'] else float(row['med_salary'])
                    remote_allowed = False if not row['remote_allowed'] else row['remote_allowed'].lower() == 'true'

                    DetailedJob.objects.create(
                        title=row['title'],
                        description=row['description'].encode('unicode_escape').decode('utf-8'),
                        med_salary=med_salary,
                        formatted_work_type=row['formatted_work_type'],
                        location=row['location'],
                        remote_allowed=remote_allowed,
                        job_posting_url=row['job_posting_url'],
                        application_type=row['application_type'],
                        skills_desc=row['skills_desc'],
                        work_type=row['work_type']
                    )
                except ValueError as e:
                    self.stdout.write(self.style.ERROR(f"Error importing job: {e}"))
        self.stdout.write(self.style.SUCCESS('Successfully imported jobs'))
