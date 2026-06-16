# Sử dụng Python (có thể đổi version 3.9, 3.10 tùy dự án của bạn)
FROM python:3.10-slim

# Tắt bộ nhớ đệm của Python để log in ra mượt hơn
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Tạo thư mục làm việc
WORKDIR /app

# Cài đặt thư viện (Cần đảm bảo bạn có file requirements.txt)
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy toàn bộ code vào container
COPY . /app/