import json
from itemadapter import ItemAdapter
from sqlalchemy import create_engine
from scrapy.exceptions import DropItem

from scraper.models import (
    metadata,
    raw_products as raw_products_table,
)


class PostgresPipeline:
    def __init__(self, database_url):
        self.engine = create_engine(database_url, future=True)
        metadata.create_all(self.engine)

    @classmethod
    def from_crawler(cls, crawler):
        db_url = crawler.settings.get("DATABASE_URL")
        if not db_url:
            raise ValueError("DATABASE_URL is not set")
        return cls(db_url)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        url = adapter.get("url")
        parsed_at = adapter.get("parsed_at")

        if not url or not parsed_at:
            raise DropItem(f"Missing required fields: {url}")

        # Сериализуем весь собранный словарь для колонки raw_data (JSONB)
        raw_payload = json.loads(json.dumps(adapter.asdict(), default=str, ensure_ascii=False))

        try:
            with self.engine.begin() as conn:
                conn.execute(
                    raw_products_table.insert().values(
                        url=url,
                        raw_data=raw_payload,
                        parsed_at=parsed_at,
                    )
                )
        except Exception as e:
            spider.logger.error(f"DB Error for URL {url}: {e}")
            raise

        spider.logger.info("Saved raw product to DB: %s", url)
        return item
