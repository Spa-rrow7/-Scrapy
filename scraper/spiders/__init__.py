# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    print("DEBUG: Spider __init__ started")  # Принудительный вывод
    try:
        self.loader = DynamicPageLoader()
        print("DEBUG: DynamicPageLoader created successfully")
    except Exception as exc:
        print(f"DEBUG: FAILED to create DynamicPageLoader: {exc}")
        self.loader = None