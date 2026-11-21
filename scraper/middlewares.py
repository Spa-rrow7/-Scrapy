import random

from twisted.internet import reactor
from twisted.internet.task import deferLater


class RotatingUserAgentMiddleware:
    """
    Выбирает User-Agent для каждого обычного HTTP-запроса.
    """

    def __init__(self, ua_list):
        self.ua_list = ua_list or []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            crawler.settings.getlist("USER_AGENT_LIST")
        )

    def process_request(self, request, spider):
        if self.ua_list and not request.meta.get("dont_rotate_ua"):
            user_agent = random.choice(self.ua_list)

            request.headers["User-Agent"] = user_agent

            spider.logger.debug(
                "User-Agent selected: %s",
                user_agent
            )


class ErrorPauseMiddleware:
    """
    Неблокирующая обработка временных HTTP-ошибок.

    Использует экспоненциальную задержку:
    5, 10, 20 секунд.

    403 не повторяется автоматически.
    """

    RETRY_HTTP_CODES = {
        408,
        429,
        500,
        502,
        503,
        504,
    }

    BASE_PAUSE = 5
    MAX_RETRY = 3

    def __init__(self, ua_list):
        self.ua_list = ua_list or []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            crawler.settings.getlist("USER_AGENT_LIST")
        )

    def process_request(self, request, spider):
        spider.logger.debug(
            "Request: %s %s",
            request.method,
            request.url
        )

    def process_response(self, request, response, spider):

        spider.logger.info(
            "Response: status=%s url=%s",
            response.status,
            response.url
        )

        if response.status == 403:
            spider.logger.warning(
                "HTTP 403: доступ запрещён, запрос не повторяется: %s",
                response.url
            )
            return response

        if response.status not in self.RETRY_HTTP_CODES:
            return response

        retry_count = request.meta.get("error_retry", 0)

        if retry_count >= self.MAX_RETRY:
            spider.logger.error(
                "Retry limit reached: status=%s url=%s",
                response.status,
                response.url
            )
            return response

        pause = self.BASE_PAUSE * (2 ** retry_count)

        spider.logger.warning(
            "HTTP %s. Retry %s/%s after %s seconds: %s",
            response.status,
            retry_count + 1,
            self.MAX_RETRY,
            pause,
            response.url
        )

        new_request = request.copy()

        new_request.dont_filter = True
        new_request.priority = request.priority - 1

        new_request.meta["error_retry"] = retry_count + 1

        # Не передаём старый HTTP-ответ в callback
        new_request.meta.pop("download_latency", None)

        if self.ua_list:
            new_request.headers["User-Agent"] = random.choice(
                self.ua_list
            )

        return deferLater(
            reactor,
            pause,
            lambda: new_request
        )
