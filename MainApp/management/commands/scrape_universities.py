from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.core.management import BaseCommand
from MainApp.models import School

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service  # 导入 Service 类

def get_driver():
    chrome_bin = os.environ.get('GOOGLE_CHROME_BIN', 'chromedriver')
    chrome_driver_path = os.environ.get('CHROMEDRIVER_PATH', '/app/.chromedriver/bin/chromedriver')

    chrome_options = Options()
    chrome_options.binary_location = chrome_bin
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # 使用 Service 指定 chromedriver 的路径
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver

class Command(BaseCommand):
    help = 'Scrape university data and save/update it in a CSV file'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to scrape university data...'))
        self.store_university_data()
        self.stdout.write(self.style.SUCCESS('Done! University data has been stored in the database.'))

    def get_university_names(self, driver, url):
        driver.get(url)
        wait = WebDriverWait(driver, 10)  # Use WebDriverWait
        university_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.uni-det h2 a:nth-child(2) > span')))
        universities = [uni.text.strip() for uni in university_elements]
        return universities

    def store_university_data(self):
        driver = get_driver()
        base_url = 'https://www.topuniversities.com/universities'
        all_universities = self.get_university_names(driver, base_url)

        pagination_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#alt-style-pagination li a.page-link'))
        )
        total_pages = int(pagination_elements[-2].text)

        for i in range(2, total_pages + 1):
            page_url = f'{base_url}/?page={i}'
            self.stdout.write(self.style.SUCCESS(f'page count: {i}'))
            all_universities.extend(self.get_university_names(driver, page_url))

        for university_name in all_universities:
            School.objects.get_or_create(name=university_name)
        self.stdout.write(self.style.SUCCESS(f'School count: {len(all_universities)}'))

        driver.quit()
