import os

from django.core.management import BaseCommand
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

from MainApp.models import School

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def get_driver():
    chrome_bin = os.environ.get('GOOGLE_CHROME_BIN', 'chromedriver')
    chrome_driver_path = os.environ.get('CHROMEDRIVER_PATH', '/app/.chromedriver/bin/chromedriver')

    chrome_options = Options()
    chrome_options.binary_location = chrome_bin
    chrome_options.add_argument("--headless")  # 运行无头模式
    chrome_options.add_argument("--disable-gpu")  # 禁用 GPU 加速
    chrome_options.add_argument("--no-sandbox")  # 运行在无沙盒模式
    chrome_options.add_argument("--disable-dev-shm-usage")  # 解决资源限制问题

    driver = webdriver.Chrome(options=chrome_options)
    return driver


class Command(BaseCommand):
    help = 'Scrape university data and save/update it in a CSV file'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to scrape university data...'))
        self.store_university_data()
        self.stdout.write(self.style.SUCCESS('Done! University data has been stored in the database.'))

    def get_university_names(self, driver, url):
        driver.get(url)
        time.sleep(5)  # Wait for JavaScript rendering
        universities = []
        university_elements = driver.find_elements(By.CSS_SELECTOR, 'div.uni-det h2 a:nth-child(2) > span')
        for uni in university_elements:
            universities.append(uni.text.strip())  # Strip to remove any leading/trailing whitespace
        return universities

    def store_university_data(self):
        driver = get_driver()
        base_url = 'https://www.topuniversities.com/universities'

        all_universities = self.get_university_names(driver, base_url)

        # Loop through all pages
        driver.get(base_url)
        time.sleep(5)
        pagination_elements = driver.find_elements(By.CSS_SELECTOR, '#alt-style-pagination li a.page-link')
        total_pages = int(pagination_elements[-2].text)
        self.stdout.write(self.style.SUCCESS(f'Got total pages: {total_pages}'))
        for i in range(2, total_pages + 1):  # Loop through all pages
            page_url = f'{base_url}/?page={i}'
            all_universities.extend(self.get_university_names(driver, page_url))

        # Store data in the database

        for university_name in all_universities:
            School.objects.get_or_create(name=university_name)
        self.stdout.write(self.style.SUCCESS(f'school account {all_universities.count()}'))

        driver.quit()
