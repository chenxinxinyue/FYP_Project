from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 设置Django的默认设置模块。
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FYP_Project.settings')

app = Celery('FYP_Project')

# 使用Django的设置文件配置Celery。
app.config_from_object('django.conf:settings', namespace='CELERY')

# 从所有已注册的Django app configs加载task模块。
app.autodiscover_tasks()
