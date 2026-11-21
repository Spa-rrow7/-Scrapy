# ETL Pipeline: Scrapy + Selenium + PostgreSQL + PySpark

Учебный проект по созданию ETL-пайплайна для сбора и анализа данных с интернет-магазина музыкальных инструментов [SKIFMUSIC](https://skifmusic.ru/).

## 🛠 Стек технологий
- **Scrapy** + **Selenium** (сбор данных и обход динамического контента)
- **PostgreSQL** (хранение в Docker)
- **SQLAlchemy** (модели данных)
- **PySpark** + **Jupyter** (очистка, нормализация, трансформация)

## 📂 Структура проекта
- `scraper/` — код паука Scrapy, модели SQLAlchemy, пайплайны и настройки.
- `Spark.ipynb` — Jupyter Notebook с PySpark ETL.
- `logs/scrapy.log` — полный лог успешного парсинга.
- `DBeaver/` — скриншоты из DBeaver (доказательство выполнения задания).
- `.env.example` — шаблон для переменных окружения.


