import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
# Пути проекта
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")

# Отключаем встроенный LOG_FILE Scrapy, чтобы он не перехватывал вывод
LOG_FILE = None

# Настраиваем одновременную запись в файл и вывод в консоль
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / "scrapy.log", mode="a", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
    force=True,
)

# Scrapy
BOT_NAME = "scraper"

SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

ADDONS = {}

# Основные настройки
ROBOTSTXT_OBEY = False
FEED_EXPORT_ENCODING = "utf-8"

TELNETCONSOLE_ENABLED = False

# Скорость парсинга
CONCURRENT_REQUESTS = 2
CONCURRENT_REQUESTS_PER_DOMAIN = 1

DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_TIMEOUT = 60

# Автоматическое регулирование нагрузки
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 30
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
AUTOTHROTTLE_DEBUG = True

# Повторные запросы
RETRY_ENABLED = True
RETRY_TIMES = 3

RETRY_HTTP_CODES = [
    408,
    429,
    500,
    502,
    503,
    504,
]

RETRY_PRIORITY_ADJUST = -1

# User-Agent
USER_AGENT_LIST = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.0 Safari/605.1.15"
    ),
]

# Downloader Middleware
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,

    "scraper.middlewares.RotatingUserAgentMiddleware": 400,
    "scraper.middlewares.ErrorPauseMiddleware": 550,

    "scrapy_selenium.SeleniumMiddleware": 800,
}


# Selenium
SELENIUM_DRIVER_NAME = "chrome"

SELENIUM_DRIVER_EXECUTABLE_PATH = os.getenv(
    "CHROMEDRIVER_PATH",
    r"C:\Users\User\.cache\selenium\chromedriver\win64\158.0.8127.36\chromedriver.exe",
)

SELENIUM_DRIVER_ARGUMENTS = [
    "--headless=new",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--window-size=1920,1080",
]

SELENIUM_IMPLICIT_WAIT = 5
SELENIUM_PAGE_LOAD_TIMEOUT = 60

# Item Pipelines
ITEM_PIPELINES = {
    "scraper.pipelines.PostgresPipeline": 300,
}

# PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL is not set. "
        "Check your .env file."
    )

# Логирование
LOG_ENABLED = True
LOG_LEVEL = "INFO"
LOG_ENCODING = "utf-8"
LOG_FORMAT = (
    "%(asctime)s [%(levelname)s] "
    "%(name)s: %(message)s"
)

LOGSTATS_INTERVAL = 30
STATS_DUMP = True

# Логирование всех запросов и ответов
LOG_REQUESTS = True
LOG_RESPONSES = True

# Статистика и память
MEMUSAGE_ENABLED = True
MEMUSAGE_WARNING_MB = 1024
MEMUSAGE_LIMIT_MB = 1536

# Прочее
COOKIES_ENABLED = True
REDIRECT_ENABLED = True
HTTPERROR_ALLOW_ALL = False
