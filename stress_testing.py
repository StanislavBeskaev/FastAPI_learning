import threading
import time

import requests
from loguru import logger


RESOURCE_URL = 'http://127.0.0.1:8000/notes/'
success_count = 0


class StressTestingHandler(threading.Thread):
    def __init__(self, interval: int):
        super().__init__()
        self.interval = interval
        self.counter = 0
        logger.info(f'Поток {self.name} начал работать')

    def run(self):
        global success_count
        start = time.monotonic()
        delta = 0
        while delta < self.interval:
            try:
                requests.get(RESOURCE_URL)
                self.counter += 1
                success_count += 1
            except:
                pass
            finally:
                delta = time.monotonic() - start

        logger.debug(f'Поток {self.name} работал {self.interval} секунд выполнил {self.counter} запросов.'
                     f' Rate {self.counter/self.interval}')


def make_stress_testing(thread_count: int = 10, interval: int = 60):
    logger.info(f"Старт. Количество потоков {thread_count}, интервал {interval} секунд, endpoint: {RESOURCE_URL}")
    threads = []
    for i in range(0, thread_count):
        thread = StressTestingHandler(interval=interval)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
    logger.info(f"Финиш. {thread_count} потоков/{interval} секунд."
                f" Общее количество запросов составило: {success_count}. Rate {success_count/interval}")


if __name__ == "__main__":
    make_stress_testing(thread_count=3, interval=10)
