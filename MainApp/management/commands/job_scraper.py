from django.core.management.base import BaseCommand
import csv
from jobspy import scrape_jobs


# 注意：这个命令现在期望从命令行接收一个位置参数
class Command(BaseCommand):
    help = 'Scrape job listings and save to CSV'

    def add_arguments(self, parser):
        parser.add_argument('location', type=str, help='Location for job search')

    def handle(self, *args, **options):
        location = options['location']
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
            search_term="software engineer",
            location=location,
            results_wanted=20,
            hours_old=72,
            country_indeed='USA'
        )
        print(f"Found {len(jobs)} jobs")
        # 确保目录存在
        jobs.to_csv("static/file/jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
        self.stdout.write(self.style.SUCCESS(f'Successfully scraped job listings for {location}'))
