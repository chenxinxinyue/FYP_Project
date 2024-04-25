"""
    use Django and Selenium to scrape the university names from the website

"""
import os

from django.core.management import BaseCommand
from selenium import webdriver  # Part of the Selenium library that automates web page operations
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from MainApp.models import School


def get_driver():
    """
    This function config and returns a Selenium WebDriver object
    that controls the Chrome browser.
    The path determine the location of the Chrome executable and Chromedriver. (in heroku)
    Configuration includes enabling headless mode and some other options to
    optimize the runtime environment, improve performance and compatibility
    during automated testing or data scraping
    :return:
    """
    # from heroku
    chrome_bin = os.environ.get('GOOGLE_CHROME_BIN', 'chromedriver')
    chrome_driver_path = os.environ.get('CHROMEDRIVER_PATH', '/app/.chromedriver/bin/chromedriver')

    chrome_options = Options()
    chrome_options.binary_location = chrome_bin
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Specify the chromedriver path with Service
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver


def get_university_names(driver, url):
    """
    Load a new page with the webdriver, then set up the wait function and keep checking
    until there is at least one element that meets the condition
    :param driver:
    :param url:
    :return:
    """
    driver.get(url)
    wait = WebDriverWait(driver, 10)  # Use WebDriverWait
    university_elements = wait.until(
        # # univListingCards > div:nth-child(13) > div > div > div.card-wrap > div.card-body >
        # div.uni-det > h2 > a:nth-child(2) > span
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.uni-det h2 a:nth-child(2) > span')))
    universities = [uni.text.strip() for uni in university_elements]
    return universities


class Command(BaseCommand):
    help = 'Scrape university data'

    """
    handle(): the entry point for the command
    """

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to scrape university data...'))
        self.store_university_data()
        self.stdout.write(self.style.SUCCESS('Done! University data has been stored in the database.'))

    def store_university_data(self):
        driver = get_driver()
        base_url = 'https://www.topuniversities.com/universities'
        all_universities = get_university_names(driver, base_url)
        # #alt-style-pagination > li.active > span
        pagination_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '#alt-style-pagination li a.page-link'))
        )
        total_pages = int(pagination_elements[-2].text)

        for i in range(2, total_pages + 1):
            page_url = f'{base_url}/?page={i}'
            self.stdout.write(self.style.SUCCESS(f'page count: {i}'))
            all_universities.extend(get_university_names(driver, page_url))

        for university_name in all_universities:
            School.objects.get_or_create(name=university_name)
        self.stdout.write(self.style.SUCCESS(f'School count: {len(all_universities)}'))

        driver.quit()
