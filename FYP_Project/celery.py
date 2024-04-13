from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 这里指定你的 Django 设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FYP_Project.settings')

# 创建 Celery 应用实例，名称通常与项目名称相同
app = Celery('FYP_Project')

# 从 Django 的 settings 文件中加载配置，使用 'CELERY' 作为配置的命名空间前缀
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动从所有已注册的 Django app 中发现任务
app.autodiscover_tasks()
