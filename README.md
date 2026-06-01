# 🌿 Hoakieng Hoàng Nam E-commerce Platform

[![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Celery](https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Redis](https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)

A production-grade, containerized e-commerce platform engineered for a real-world local plant business. This system digitalizes daily inventory operations, securely processes live customer traffic, and utilizes asynchronous microservices to ensure lightning-fast checkout experiences.

**[View Live Website](https://hoakienghoangnam.id.vn/) | [Report Bug](https://github.com/vietnguyeen/GreenShop---Tree-Selling-Shop/issues)**

---

## 🚀 System Architecture & Tech Stack

This project strictly follows the 12-Factor App methodology, separating the infrastructure into isolated, scalable services using **Docker Compose**.

*   **Backend Framework:** Python (Django)
*   **Database:** PostgreSQL
*   **Message Broker & Caching:** Redis
*   **Asynchronous Workers:** Celery
*   **Web Server / Reverse Proxy:** Caddy (Automated SSL/TLS)
*   **CI/CD Pipeline:** GitHub Actions
*   **Deployment:** Ubuntu Linux VPS

## ✨ Key Features

*   **Asynchronous Task Processing:** Critical bottlenecks (like order processing and email notifications) are offloaded to **Celery** background workers via **Redis**, reducing API latency and ensuring instant page loads during checkout.
*   **Double-Layer Security Validation:** Prevents fraudulent out-of-stock purchases. The UI dynamically disables purchase buttons, while the backend strictly blocks and validates database inventory before transaction approval.
*   **Zero-Downtime CI/CD:** Automated GitHub Actions workflows handle secure SSH remote connections, source code synchronization, and container rebuilds on every push to the `main` branch.
*   **Secure Infrastructure:** Caddy acts as a reverse proxy to handle automatic HTTPS, while an internal Docker network completely isolates the PostgreSQL database and Redis broker from the public internet.

---

## 📂 Project Structure

The repository is organized with a clear separation of concerns. The outer workspace holds deployment configurations, while the core Django application resides in the `plant_shop` directory.

```text
GREENSHOP/
├── .github/workflows/    # CI/CD pipelines (deploy.yaml)
├── plant_shop/           # Core Django settings (settings.py, celery.py, wsgi.py)
├── store/                # Main application logic (models, views, templates)
├── media/                # Persistent volume for user-uploaded plant images
├── .env.example          # Template for environment variables
├── docker-compose.yml    # Multi-container orchestration
├── Dockerfile            # Web app container build instructions
└── requirements.txt      # Python dependencies
