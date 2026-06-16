from django.contrib import admin
from django.apps import apps

# Quét và lấy tất cả các models đang có trong app 'store'
app_models = apps.get_app_config('store').get_models()

# Tự động đăng ký hiển thị tất cả lên Admin
for model in app_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass