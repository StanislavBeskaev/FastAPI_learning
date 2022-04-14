import os

from fastapi import FastAPI, File, UploadFile, Form
from loguru import logger


app = FastAPI()
logger.add("log.txt")

FILES_FOLDER = "files"


def check_files_folder(func):
    def wrapper(*args, **kwargs):
        if not os.path.exists(FILES_FOLDER):
            logger.debug(f"Создана папка под файлы {FILES_FOLDER}")
            os.mkdir(FILES_FOLDER)

        return func(*args, **kwargs)

    return wrapper


@check_files_folder
def write_text_file(file: UploadFile, encoding: str) -> str:
    file_path = get_file_path(file.filename)
    with open(file_path, mode="w") as writable_file:
        content = file.file.read().decode(encoding=encoding)
        writable_file.write(content)

    logger.debug(f"Текстовый файл {file.filename} записан в {file_path}")

    return file_path


def get_file_path(file_name: str) -> str:
    return os.path.join(FILES_FOLDER, file_name)


@check_files_folder
def write_binary_file(file: UploadFile) -> str:
    file_path = get_file_path(file.filename)
    with open(file_path, mode="wb") as writable_file:
        writable_file.write(file.file.read())

    logger.debug(f"Бинарный файл {file.filename} записан в {file_path}")

    return file_path


@app.post("/files/")
async def create_file(file: bytes = File(...)):  # так файл будет преобразован в байты
    return {"file_size": len(file)}


@app.post("/upload_text_file/")
async def upload_text_file(file: UploadFile, encoding: str = Form('utf-8')):  # а так в объект
    logger.debug(f"incoming file attrs: {file.__dict__}")

    return {"filepath": write_text_file(file, encoding)}


@app.post("/upload_binary_file/")
async def upload_binary_file(file: UploadFile):
    logger.debug(f"incoming file attrs: {file.__dict__}")

    return {"filepath": write_binary_file(file)}
