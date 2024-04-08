import csv
from jobspy import scrape_jobs
from django.core.management.base import BaseCommand
import pandas as pd  # 确保导入 pandas


class Command(BaseCommand):
    help = 'Scrape job listings for multiple job preferences and save to CSV'

    def add_arguments(self, parser):
        parser.add_argument('location', type=str, help='Location for job search')
        # 修改为接受多个搜索词
        parser.add_argument('--job-preferences', nargs='+', type=str, help='List of preferred jobs')

    def handle(self, *args, **options):
        location = options['location']
        job_preferences = options.get('job_preferences', [])
        all_jobs = []  # 用于存储所有搜索词的工作列表

        # 对每个搜索词分别进行爬取
        for preference in job_preferences:
            jobs = scrape_jobs(
                site_name=["indeed", "linkedin", "zip_recruiter", "glassdoor"],
                search_term=preference,  # 使用当前的搜索词
                location=location,
                results_wanted=20,
                hours_old=72,
                country_indeed='UK',
            )
            # 将结果添加到 all_jobs 列表
            if jobs is not None:
                all_jobs.append(jobs)
            self.stdout.write(self.style.SUCCESS(f'Found {len(jobs)} jobs for {preference}'))

        # 合并所有的工作列表
        if all_jobs:
            combined_jobs = pd.concat(all_jobs, ignore_index=True)
            # 确保目录存在后保存到 CSV
            combined_jobs.to_csv("static/file/jobs.csv", quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
            self.stdout.write(self.style.SUCCESS(
                f'Successfully scraped job listings for {location} with preferences: {job_preferences}'))
        else:
            self.stdout.write(self.style.ERROR('No jobs found for the given preferences.'))
