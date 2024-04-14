from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.management import call_command

logger = get_task_logger(__name__)


@shared_task(bind=True)
def scrape_jobs_task(self, location, job_preferences_list, user_id, site_names):
    try:
        call_command('job_scraper', location, job_preferences=job_preferences_list, user_id=user_id,
                     site_names=site_names)
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        self.update_state(
            state='FAILURE',
            meta={'exc_type': type(e).__name__, 'exc_message': str(e)}
        )
        # 尝试任务重试
        raise self.retry(exc=e, max_retries=3, countdown=60)
