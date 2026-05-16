"""
Django Management Command – tạo 3 Category và toàn bộ cây mẫu.

Chạy bằng lệnh:
    python manage.py load_data

Lệnh này dùng get_or_create nên an toàn khi chạy nhiều lần (idempotent).
"""

from django.core.management.base import BaseCommand
from store.models import Category, Plant


# ── Dữ liệu mẫu theo đúng yêu cầu ────────────────────────────────────────────
SEED_DATA = {
    'Cây ăn quả': [
        'Me',
        'Khế',
        'Sakê',
    ],
    'Hoa': [
        'Bông Giấy',
        'Mai Chiếu Thủy',
        'Sứ',
        'Mai Vạn Phúc (Mai Tiểu Thư)',
        'Tuyết Mai',
        'Cúc Bách Hợp',
        'Lài',
        'Nguyệt Quới',
    ],
    'Cây xanh': [
        'Cây Xanh',
        'Hồng Lộc',
        'Trúc Nhật',
        'Hạnh Phúc',
        'Lộc Vừng',
        'Lưỡi Hổ',
        'Cau',
        'Lá Trắng',
        'Phát Tài',
        'Cọ',
    ],
}


class Command(BaseCommand):
    help = 'Tạo sẵn 3 Category và dữ liệu cây mẫu cho GreenShop.'

    def handle(self, *args, **kwargs):
        total_categories = 0
        total_plants     = 0

        for category_name, plant_names in SEED_DATA.items():

            # ── Tạo hoặc lấy Category ─────────────────────────────────────
            category, cat_created = Category.objects.get_or_create(
                name=category_name
            )
            if cat_created:
                total_categories += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ Đã tạo danh mục: "{category_name}"')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'  ⚠️  Danh mục đã tồn tại: "{category_name}"')
                )

            # ── Tạo hoặc bỏ qua từng cây ──────────────────────────────────
            for plant_name in plant_names:
                plant, plant_created = Plant.objects.get_or_create(
                    name=plant_name,
                    category=category,
                    defaults={
                        'price':    0,
                        'stock':    10,
                        'girth':    '',
                        'height':   '',
                        'diameter': '',
                    }
                )
                if plant_created:
                    total_plants += 1
                    self.stdout.write(f'      🌿 Thêm cây: {plant_name}')
                else:
                    self.stdout.write(f'      – Bỏ qua (đã có): {plant_name}')

        # ── Tổng kết ──────────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Hoàn tất! Đã tạo {total_categories} danh mục mới '
            f'và {total_plants} cây mới.'
        ))