from django.core.management.base import BaseCommand
from MainApp.models import Job
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
                Job.objects.create(
                    name=row['title'],
                    description=row['description'].encode('unicode_escape').decode('utf-8'),
                    detail_url=row['job_posting_url']
                )
        self.stdout.write(self.style.SUCCESS('Successfully imported jobs'))
