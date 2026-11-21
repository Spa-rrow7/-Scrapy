import re
from datetime import datetime, timezone

import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scraper.items import ProductItem


def clean_text(value):
    if not value:
        return None
    value = " ".join(value.split())
    return value if value else None


def to_float(value):
    if value is None:
        return None
    try:
        clean_val = (
            str(value)
            .replace(",", ".")
            .replace(" ", "")
            .replace("\xa0", "")
            .replace("₽", "")
            .strip()
        )
        return float(clean_val)
    except ValueError:
        return None


def to_int(value):
    if value is None:
        return None
    m = re.search(r"\d+", str(value))
    return int(m.group()) if m else None


class ShopforgeSpider(scrapy.Spider):
    name = "shopforge"
    allowed_domains = ["skifmusic.ru"]

    base_url = "https://skifmusic.ru/catalog/gitaryi-1"
    max_pages = 5

    async def start(self):
        yield SeleniumRequest(
            url=self.base_url,
            callback=self.parse_catalog,
            wait_time=10,
            wait_until=EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.product-card")
            ),
            meta={"page_num": 1},
        )

    def parse_catalog(self, response):
        """Собирает ссылки со всех страниц каталога через AJAX-пагинацию Selenium."""
        driver = response.meta.get("driver")
        seen_links = set()

        for page_num in range(1, self.max_pages + 1):
            if driver:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.85);")
                response = response.replace(body=driver.page_source)

            cards = response.css("div.product-card")
            new_links = []
            for card in cards:
                href = card.css("a.product-card__image::attr(href), a[href*='/product/']::attr(href)").get()
                if href:
                    full_url = response.urljoin(href)
                    if full_url not in seen_links:
                        seen_links.add(full_url)
                        new_links.append(full_url)

            self.logger.info(
                "Страница каталога %s: всего карточек в DOM=%s, новых товаров=%s",
                page_num, len(cards), len(new_links)
            )

            for link in new_links:
                yield SeleniumRequest(
                    url=link,
                    callback=self.parse_product,
                    wait_time=10,
                    wait_until=EC.presence_of_element_located((By.CSS_SELECTOR, "h1")),
                )

            # Если это не последняя страница — жмем "Показать еще" или "Следующая страница"
            if page_num < self.max_pages and driver:
                try:
                    prev_count = len(cards)
                    next_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH,
                             "//button[contains(., 'Показать еще')] | //a[contains(., 'Показать еще')] | //a[contains(., 'Следующая страница')]")
                        )
                    )
                    driver.execute_script("arguments[0].click();", next_btn)

                    # Ждем подгрузки новых карточек (AJAX)
                    WebDriverWait(driver, 15).until(
                        lambda d: len(d.find_elements(By.CSS_SELECTOR, "div.product-card")) > prev_count
                                  or str(page_num + 1) in d.current_url
                    )
                except Exception as e:
                    self.logger.warning("Пагинация завершилась на странице %s: %s", page_num, e)
                    break

    def parse_product(self, response):
        """Извлекает данные со страницы товара (PDP)."""
        driver = response.meta.get("driver")
        if driver:
            # 1. Прокрутка страницы (требование ТЗ: window.scrollTo)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 2);")

            # 2. Ожидание и клик по вкладке "Характеристики" (требование ТЗ: WebDriverWait)
            try:
                char_tab = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[contains(., 'Характеристики')] | //a[contains(., 'Все характеристики')] | //div[contains(@class, 'tab') and contains(., 'Характеристики')]")
                    )
                )
                driver.execute_script("arguments[0].click();", char_tab)
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//*[contains(text(), 'Артикул') or contains(text(), 'Страна производства')]")
                    )
                )
            except Exception as e:
                self.logger.warning(f"Вкладка характеристик не раскрыта на {response.url}: {e}")

            # 3. Прокрутка ниже к отзывам и обновление DOM
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.8);")
            response = response.replace(body=driver.page_source)

        item = ProductItem()
        item["url"] = response.url
        item["parsed_at"] = datetime.now(timezone.utc).isoformat()

        # --- 1. Название ---
        item["title"] = clean_text(response.css("h1::text").get())

        # --- 2. Цена ---
        price_text = response.css("p.product-card-info__price::text").get()
        item["price"] = to_float(price_text)

        # --- 3. Рейтинг и количество отзывов ---
        rating_stars = response.css("span.product-card-info__stars-value::text").get()
        if rating_stars:
            rating_match = re.search(r"([\d.,]+)", rating_stars)
            count_match = re.search(r"\((\d+)\)", rating_stars)
            item["rating"] = to_float(rating_match.group(1)) if rating_match else None
            item["reviews_count"] = to_int(count_match.group(1)) if count_match else 0
        else:
            item["rating"] = None
            item["reviews_count"] = 0

        # --- 4. Характеристики (верхний блок + полная вкладка на 22 пункта) ---
        characteristics = {}
        # 4.1 Краткий блок
        for group in response.css(".product-info-group"):
            key = clean_text(group.css(".product-info-group__title::text").get())
            value_parts = group.css(".product-info-group__items *::text").getall()
            value = clean_text(" ".join(value_parts))
            if key and value:
                characteristics[key.rstrip(":")] = value

        # 4.2 Полный список во вкладке "Характеристики" (элементы формата "Ключ: Значение")
        for li in response.css("li"):
            li_text = clean_text(" ".join(li.css("*::text, ::text").getall()))
            if li_text and ":" in li_text and len(li_text) < 120:
                k, v = li_text.split(":", 1)
                k, v = clean_text(k), clean_text(v)
                if k and v and k not in {"Москва", "ID"}:
                    characteristics[k] = v

        item["characteristics"] = characteristics

        # --- 5. Описание ---
        desc_parts = response.css(".product-description *::text, [itemprop='description'] *::text").getall()
        item["description"] = clean_text(" ".join(desc_parts)) or item["title"]

        # --- 6. Отзывы (вложенная структура для таблицы reviews) ---
        comments = []
        for idx, rev in enumerate(response.css("[class*='review-item'], [class*='reviews__item'], .review"), start=1):
            author = clean_text(rev.css("[class*='author']::text, [class*='name']::text").get())
            text = clean_text(" ".join(rev.css("[class*='text'] *::text, [class*='comment'] *::text, p::text").getall()))
            if author and text:
                comments.append({
                    "review_id": f"{characteristics.get('Код товара', 'item')}_{idx}",
                    "author": author,
                    "rating": item["rating"] or 5,
                    "title": None,
                    "text": text,
                    "verified": True,
                    "date": None,
                    "helpful": 0,
                })
        item["comments"] = comments
        item["questions"] = []

        # --- 7. Категории (хлебные крошки) ---
        breadcrumbs = [
            clean_text(t) for t in response.css("ul.breadcrumbs a::text, .breadcrumb a::text").getall()
            if clean_text(t) and clean_text(t) not in {"Главная", "Каталог"}
        ]
        item["category"] = breadcrumbs or ["Гитары"]

        # --- 9. Основные поля ---
        item["sku"] = characteristics.get("Код товара") or characteristics.get("Артикул")
        item["brand"] = characteristics.get("Производитель") or "Не указан"
        item["seller"] = "SKIFMUSIC"
        item["condition"] = characteristics.get("Состояние", "Новое")
        item["availability"] = "In Stock"

        yield item
