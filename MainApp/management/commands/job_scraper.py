import pandas as pd  # Ensure pandas is imported
from django.core.management.base import BaseCommand
from jobspy import scrape_jobs


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
        self.stdout.write(self.style.ERROR(f'{country_indeed}'))

        for preference in job_preferences:
            if site_names and ('indeed' in site_names or 'glassdoor' in site_names):
                jobs = scrape_jobs(
                    site_name=site_names,
                    search_term=preference,
                    location=location,
                    results_wanted=20,
                    hours_old=72,
                    country_indeed=country_indeed,
                )
            else:
                jobs = scrape_jobs(
                    site_name=site_names,
                    search_term=preference,
                    location=location,
                    results_wanted=20,
                    hours_old=72
                )

            if jobs is not None:
                all_jobs.append(jobs)

        if all_jobs:
            combined_jobs = pd.concat(all_jobs, ignore_index=True)
            file_name = f"static/file/jobs_{user_id}.csv"
            combined_jobs.to_csv(file_name, index=False)
            self.stdout.write(self.style.SUCCESS(f'Job listings saved to {file_name}'))
        else:
            self.stdout.write(self.style.ERROR('No jobs found for the given preferences.'))
