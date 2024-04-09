import csv
from jobspy import scrape_jobs
from django.core.management.base import BaseCommand
import pandas as pd  # 确保导入 pandas


class Command(BaseCommand):
    help = 'Scrape job listings for multiple job preferences and save to CSV'

    def add_arguments(self, parser):
        parser.add_argument('location', type=str, help='Location for job search')
        parser.add_argument('--job-preferences', nargs='+', type=str, help='List of preferred jobs')
        # 添加用户 ID 参数
        parser.add_argument('--user-id', type=int, help='User ID')

    def handle(self, *args, **options):
        location = options['location']
        job_preferences = options.get('job_preferences', [])
        user_id = options.get('user_id')  # 获取用户 ID
        all_jobs = []

        for preference in job_preferences:
            jobs = scrape_jobs(
                site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
                search_term=preference,
                location=location,
                results_wanted=20,
                hours_old=72,
                country_indeed='UK',
            )
            if jobs is not None:
                all_jobs.append(jobs)
            self.stdout.write(self.style.SUCCESS(f'Found {len(jobs)} jobs for {preference}'))

        if all_jobs:
            combined_jobs = pd.concat(all_jobs, ignore_index=True)
            # 使用用户 ID 构造文件名
            file_name = f"static/file/jobs_{user_id}.csv"
            combined_jobs.to_csv(file_name, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
            self.stdout.write(self.style.SUCCESS(
                f'Successfully scraped job listings for {location} with preferences: {job_preferences} and saved to {file_name}'))
        else:
            self.stdout.write(self.style.ERROR('No jobs found for the given preferences.'))
