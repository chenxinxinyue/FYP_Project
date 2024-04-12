from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
import time
from MainApp.models import School  # Replace 'yourapp' with the name of your Django app


class Command(BaseCommand):
    help = 'Scrape university data and save/update it in the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to scrape university data...'))
        self.store_university_data()
        self.stdout.write(self.style.SUCCESS('Done! University data has been stored in the database.'))

    def get_university_names(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        universities = []
        university_elements = soup.select('div.uni-det h2 a:nth-child(2) > span')
        for uni in university_elements:
            universities.append(uni.text.strip())
        return universities

    def store_university_data(self):
        base_url = 'https://www.topuniversities.com/universities'
        all_universities = self.get_university_names(base_url)

        # Loop through all pages
        response = requests.get(base_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        pagination_elements = soup.select('#alt-style-pagination li a.page-link')
        total_pages = int(pagination_elements[-2].text)
        self.stdout.write(self.style.SUCCESS(f'Got total pages: {total_pages}'))

        for i in range(2, total_pages + 1):  # Loop through all pages
            page_url = f'{base_url}/?page={i}'
            all_universities.extend(self.get_university_names(page_url))

        # Store data in the database
        for university_name in all_universities:
            School.objects.get_or_create(name=university_name)
