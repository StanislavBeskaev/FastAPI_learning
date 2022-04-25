# Запуск dev сервера через uvicorn
`uvicorn <модуль>:<приложение FastAPI> -- reload`  
Если модуль main и приложение app то:  
`uvicorn main:app --reload`

## Документация
Доступна по `/docs`

## Документация в формате OpenAPI
Доступна по `/openapi.json`


## Тесты
Выполнить `pytest`

## Code coverage
Собрать статистику покрытия: `coverage run -m unittest`
Отчёт о покрытии в консоли: `coverage report -m`
Отчёт о покрытии в html: `coverage html`