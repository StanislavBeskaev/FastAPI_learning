import asyncio
import json
import time
from pydantic import BaseModel

import aiohttp
from loguru import logger


class TestResult(BaseModel):
    url: str
    interval: int
    task_count: int
    responses_amount: int
    rate: float
    tasks_result: str


async def stress_testing(task_id: int, session, interval: int, url: str):
    logger.debug(f"Task {task_id} начала работать")

    counter = 0
    start = time.monotonic()
    delta = 0
    while delta < interval:
        async with session.get(url) as response:
            await response.json()
            counter += 1
        delta = time.monotonic() - start

    logger.debug(f'Task {task_id} работала {interval} секунд выполнил {counter} запросов.'
                 f' Rate {counter / interval}')
    return task_id, counter


async def main():
    results_file = "async_stress_testing.json"
    resource_url = 'http://127.0.0.1:8000/notes/'
    interval = 10
    max_task_count = 20
    task_step = 1
    logger.info(f"Тест {resource_url}, интервал: {interval},"
                f" максимальное количество tasks {max_task_count}, шаг {task_step}")

    test_results = []

    async with aiohttp.ClientSession() as session:
        for task_count in range(1, max_task_count + 1, task_step):
            tasks = []
            for i in range(1, task_count + 1):
                tasks.append(asyncio.ensure_future(stress_testing(
                    task_id=i,
                    session=session,
                    interval=interval,
                    url=resource_url
                )))
            logger.info(f"Старт. Количество tasks {task_count}, интервал {interval} секунд, endpoint: {resource_url}")
            results = await asyncio.gather(*tasks)
            results = sorted(results, key=lambda result: result[0])
            responses_amount = sum([result[1] for result in results])
            tasks_result = ", ".join([f"Task_{result[0]}: {result[1]}" for result in results])

            logger.info(f"Финиш. {task_count} tasks/{interval} секунд."
                        f" Общее количество запросов составило: {responses_amount}. Rate {responses_amount / interval}"
                        f" По tasks: {tasks_result}")

            test_results.append(
                TestResult(
                    url=resource_url,
                    interval=interval,
                    task_count=task_count,
                    responses_amount=responses_amount,
                    rate=responses_amount/interval,
                    tasks_result=tasks_result
                ).dict()
            )

    with open(results_file, mode='w', encoding='utf-8') as file:
        json.dump(obj=test_results, fp=file, indent=2, ensure_ascii=False)

    logger.info(f"Результаты записаны в файл: {results_file}")

asyncio.run(main())
