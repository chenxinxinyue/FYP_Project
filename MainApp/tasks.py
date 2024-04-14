from celery import shared_task
from django.core.management import call_command

@shared_task
def scrape_jobs_task(location, job_preferences_list, user_id, site_names, country_indeed):
    call_command('job_scraper', location, job_preferences=job_preferences_list, user_id=user_id,
                 site_names=site_names, country_indeed=country_indeed)
