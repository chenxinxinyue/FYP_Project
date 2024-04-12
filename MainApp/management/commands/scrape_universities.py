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
        print(uni.text)  # 输出学校名称文本而不是WebElement对象
    return universities


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
        all_universities = get_university_names(driver, base_url)

        # 获取总页数
        driver.get(base_url)
        time.sleep(5)
        pagination_elements = driver.find_elements(By.CSS_SELECTOR, '#alt-style-pagination li a.page-link')
        total_pages = int(pagination_elements[-2].text)  # 倒数第二个元素包含最后一页的页码

        # 循环遍历所有页面
        for i in range(2, total_pages + 1):
            page_url = f'{base_url}/?page={i}'
            all_universities.extend(get_university_names(driver, page_url))

        # 将所有学校名称写入CSV文件
        with open('universities.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['University Name'])  # 写入表头
            for university in all_universities:
                writer.writerow([university])  # 写入学校名称

        # Dummy data for demonstration:
        data = ['University of Example', 'Sample State University']
        driver.quit()
        return data

    def write_to_csv(self, filename, data):
        mode = 'w' if os.path.exists(filename) else 'w'
        with open(filename, mode, newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['University Name'])
            for university in data:
                writer.writerow([university])
