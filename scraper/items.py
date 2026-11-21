import scrapy


class ProductItem(scrapy.Item):

    # Обязательные поля
    url = scrapy.Field()
    parsed_at = scrapy.Field()

    # Основная информация
    sku = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()

    # Текстовые структуры
    category = scrapy.Field()
    brand = scrapy.Field()

    # Цены
    price = scrapy.Field()

    # Рейтинг
    rating = scrapy.Field()
    reviews_count = scrapy.Field()

    # Информация о продавце
    seller = scrapy.Field()
    condition = scrapy.Field()
    availability = scrapy.Field()

    # Вложенные структуры
    characteristics = scrapy.Field()
    comments = scrapy.Field()
    questions = scrapy.Field()


    # Служебные данные
    raw_data = scrapy.Field()
    parse_errors = scrapy.Field()
