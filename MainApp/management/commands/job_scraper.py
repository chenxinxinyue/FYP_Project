import csv
from jobspy import scrape_jobs
from django.core.management.base import BaseCommand
import pandas as pd  # Ensure pandas is imported


class Command(BaseCommand):
    help = 'Scrape job listings for multiple job preferences and save to CSV'

    def add_arguments(self, parser):
        parser.add_argument('location', type=str, help='Location for job search')
        parser.add_argument('--job-preferences', nargs='+', type=str, help='List of preferred jobs')
        parser.add_argument('--user-id', type=int, help='User ID')
        parser.add_argument('--site-names', nargs='+', help='List of site names to scrape jobs from')
        parser.add_argument('--country-indeed', type=str, help='Country for Indeed/Glassdoor search')

    def handle(self, *args, **options):
        location = options['location']
        site_names = options.get('site_names')
        job_preferences = options.get('job_preferences', [])
        user_id = options.get('user_id')
        country_indeed = options.get('country_indeed')
        all_jobs = []
        self.stdout.write(self.style.SUCCESS(f'country_indeed: {country_indeed}'))
        self.stdout.write(self.style.SUCCESS(f'site_names: {site_names}'))

        for site_name in site_names:
            for preference in job_preferences:
                if site_name.lower() in ['indeed', 'glassdoor']:
                    jobs = scrape_jobs(
                        site_name=site_name,
                        search_term=preference,
                        location=location,
                        results_wanted=20,
                        hours_old=72,
                        country_indeed=country_indeed,
                    )
                    if jobs is not None:
                        all_jobs.append(jobs)
                else:
                    # 对于LinkedIn和ZipRecruiter，不需要国家参数
                    jobs = scrape_jobs(
                        site_name=site_name,
                        search_term=preference,
                        location=location,
                        results_wanted=20,
                        hours_old=72
                    )
                    if jobs is not None:
                        all_jobs.append(jobs)

            # self.stdout.write(self.style.SUCCESS(f'Found {len(jobs)} jobs for {preference}'))

        if all_jobs:
            combined_jobs = pd.concat(all_jobs, ignore_index=True)
            file_name = f"static/file/jobs_{user_id}.csv"
            combined_jobs.to_csv(file_name, index=False)
            self.stdout.write(self.style.SUCCESS(f'Job listings saved to {file_name}'))
        else:
            self.stdout.write(self.style.ERROR('No jobs found for the given preferences.'))
