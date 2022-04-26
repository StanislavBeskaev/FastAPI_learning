import threading
import time

import requests
from loguru import logger


success_count = 0


class StressTestingHandler(threading.Thread):
    def __init__(self, interval: int, url):
        super().__init__()
        self.interval = interval
        self.counter = 0
        self.url = url
        logger.debug(f'Поток {self.name} начал работать')

    def run(self):
        global success_count
        start = time.monotonic()
        delta = 0
        while delta < self.interval:
            try:
                requests.get(self.url)
                self.counter += 1
                success_count += 1
            except:
                pass
            finally:
                delta = time.monotonic() - start

        logger.debug(f'Поток {self.name} работал {self.interval} секунд выполнил {self.counter} запросов.'
                     f' Rate {self.counter/self.interval}')


def make_stress_testing(url: str, thread_count: int = 10, interval: int = 60, ):
    logger.info(f"Старт. Количество потоков {thread_count}, интервал {interval} секунд, endpoint: {url}")
    threads = []
    for i in range(0, thread_count):
        thread = StressTestingHandler(interval=interval, url=url)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    logger.info(f"Финиш. {thread_count} потоков/{interval} секунд."
                f" Общее количество запросов составило: {success_count}. Rate {success_count/interval}")


if __name__ == "__main__":
    resource_url = 'http://127.0.0.1:8000/users/'
    interval = 10
    max_thread_count = 5
    thread_step = 1

    for thread_count in range(1, max_thread_count + 1):
        success_count = 0
        make_stress_testing(thread_count=thread_count, interval=10, url=resource_url)
