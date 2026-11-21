from sqlalchemy import (
    MetaData,
    Table,
    Column,
    BigInteger,
    Integer,
    String,
    Numeric,
    TIMESTAMP,
    Text,
    ARRAY,
    Boolean,
    ForeignKey,
    UniqueConstraint,
    func,
)

from sqlalchemy.dialects.postgresql import JSONB

metadata = MetaData()


# Исходные данные непосредственно после парсинга
raw_products = Table(
    "raw_products",
    metadata,

    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("url", Text, nullable=False),
    Column("raw_data", JSONB, nullable=False),
    Column(
        "parsed_at",
        TIMESTAMP(timezone=True),
        nullable=False,
    ),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
)


# Основная таблица товаров
products = Table(
    "products",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("url", Text, nullable=False, unique=True),
    Column("sku", String(64), index=True),
    Column("title", Text),
    Column("description", Text),
    Column("category", ARRAY(Text)),
    Column("brand", String(128)),
    Column("price", Numeric(12, 2)),
    Column("rating", Numeric(3, 2)),
    Column("reviews_count", Integer),
    Column("seller", String(256)),
    Column("condition", String(64)),
    Column("availability", String(32)),

    # JSONB вместо TEXT
    Column("characteristics", JSONB),

    Column("image_urls", ARRAY(Text)),

    Column(
        "parsed_at",
        TIMESTAMP(timezone=True),
        nullable=False,
    ),

    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
)


# Отзывы покупателей
reviews = Table(
    "reviews",
    metadata,

    Column("id", BigInteger, primary_key=True, autoincrement=True),

    Column(
        "product_url",
        Text,
        ForeignKey("products.url", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),

    Column("review_id", String(128)),
    Column("author", String(128)),
    Column("rating", Integer),
    Column("title", Text),
    Column("text", Text),
    Column("verified", Boolean),

    Column("review_date", TIMESTAMP(timezone=True)),
    Column("helpful", Integer),

    UniqueConstraint(
        "product_url",
        "review_id",
        name="uq_review_product_review",
    ),
)



product_characteristics = Table(
    "product_characteristics",
    metadata,

    Column("id", BigInteger, primary_key=True, autoincrement=True),

    Column(
        "product_id",
        BigInteger,
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    ),

    Column("name", Text, nullable=False),
    Column("value", Text),

    UniqueConstraint(
        "product_id",
        "name",
        name="uq_product_characteristic",
    ),
)