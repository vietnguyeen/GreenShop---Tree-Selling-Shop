# 1. Sử dụng Python 3.12 (Bắt buộc cho Django 6.0+)
FROM python:3.12-slim

# 2. Thiết lập biến môi trường giúp log in ra mượt hơn và không tạo file rác .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Tạo thư mục làm việc trong container
WORKDIR /app

# 4. Cài đặt các lõi hệ thống cần thiết (Cực kỳ quan trọng cho Pillow và Psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy file requirements.txt vào trước để cài đặt
COPY requirements.txt /app/

# 6. Nâng cấp pip và cài đặt thư viện (thêm --no-cache-dir để giảm dung lượng image)
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 7. Cuối cùng, copy toàn bộ mã nguồn dự án vào container
COPY . /app/