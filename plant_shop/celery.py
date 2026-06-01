import os
from celery import Celery

# Sửa thành plant_shop.settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plant_shop.settings')

# Sửa thành plant_shop
app = Celery('plant_shop')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()