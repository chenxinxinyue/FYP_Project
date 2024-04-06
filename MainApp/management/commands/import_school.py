# schools/management/commands/import_schools.py

import csv
from django.core.management.base import BaseCommand
from MainApp.models import School


# schools/management/commands/import_schools.py


class Command(BaseCommand):
    help = 'Import schools from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csvfile', type=str, help='The path to the CSV file')

    def handle(self, *args, **kwargs):
        csvfile = kwargs['csvfile']
        with open(csvfile, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name = row[1]
                School.objects.create(name=name)
