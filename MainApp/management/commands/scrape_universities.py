from django.core.management.base import BaseCommand
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_university_names(driver, url):
    driver.get(url)
    time.sleep(5)  # 等待JavaScript渲染完毕
    universities = []
    # 提取所有学校名称
    university_elements = driver.find_elements(By.CSS_SELECTOR, 'div.uni-det h2 a:nth-child(2) > span')
    for uni in university_elements:
        universities.append(uni.text)  # 确保从WebElement中获取文本
    return universities

def get_total_pages(driver):
    # 这个函数需要根据实际页面结构编写，以下是一个示例
    pagination_element = driver.find_element(By.CSS_SELECTOR, '#alt-style-pagination li a.page-link')
    total_pages = int(pagination_element.get_attribute('innerText'))
    return total_pages

class Command(BaseCommand):
    help = 'Scrape university data and save/update it in a CSV file'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to scrape university data...'))
        filename = 'universities.csv'
        data = self.scrape_data()
        self.write_to_csv(filename, data)
        self.stdout.write(self.style.SUCCESS(f'Done! Data has been written to {filename}'))

    def scrape_data(self):
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        base_url = 'https://www.topuniversities.com/universities'

        # 获取首页的学校名称
        all_universities = get_university_names(driver, base_url)

        # 获取总页数
        total_pages = get_total_pages(driver)

        # 循环通过所有页面
        for i in range(2, total_pages + 1):  # 使用动态获取的总页数
            page_url = f'{base_url}/?page={i}'
            all_universities.extend(get_university_names(driver, page_url))

        driver.quit()
        return all_universities

    def write_to_csv(self, filename, data):
        mode = 'w' if os.path.exists(filename) else 'w'
        with open(filename, mode, newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['University Name'])
            for university in data:
                writer.writerow([university])
