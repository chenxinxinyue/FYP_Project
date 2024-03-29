import os
import django
import certifi
from django.core.mail import send_mail

import os

# 设置 SSL 证书的环境变量

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FYP_Project.settings')
django.setup()

send_mail(
    '测试邮件',
    '这是一个测试邮件的正文。',
    'recommendjob@gmail.com',
    ['c18056180805@163.com'],
    fail_silently=False,
)
