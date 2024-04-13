from celery import shared_task
from django.core.management import call_command


@shared_task(bind=True)
def job_scraper_task(self, location, job_preferences_list, user_id, site_names):
    # Suppose the task has multiple steps, update progress with current step count
    self.update_state(state='PROGRESS', meta={'current': 50, 'total': 100, 'status': 'Halfway done'})
    # your scraping code here
    return {'current': 100, 'total': 100, 'status': 'Task completed successfully'}
