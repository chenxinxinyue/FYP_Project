from celery import shared_task
from django.core.management import call_command
from django.core.exceptions import ImproperlyConfigured

@shared_task(bind=True)  # 添加 bind=True 以访问任务上下文
def scrape_jobs_task(self, location, job_preferences_list, user_id, site_names, country_indeed):
    try:
        call_command('job_scraper', location, job_preferences=job_preferences_list, user_id=user_id,
                     site_names=site_names, country_indeed=country_indeed)
    except Exception as e:
        # 通过自定义状态和错误信息更新任务状态
        self.update_state(
            state='FAILURE',
            meta={'exc_type': type(e).__name__, 'exc_message': str(e)}
        )
        # 重新抛出异常以确保任务被标记为失败
        raise
