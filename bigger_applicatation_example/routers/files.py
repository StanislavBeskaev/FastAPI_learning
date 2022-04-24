import os
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, Form
from loguru import logger

from ..dependencies import get_token_header


FILES_FOLDER = os.path.join(Path(__file__).resolve().parent.parent, "files")


router = APIRouter(
    prefix="/files",
    tags=["files"],
    dependencies=[Depends(get_token_header)],
)


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


@router.post("/upload_text_file/", description="Загрузка текстового файла")
async def upload_text_file(file: UploadFile, encoding: str = Form('utf-8')):  # а так в объект
    logger.debug(f"incoming file attrs: {file.__dict__}")

    write_text_file(file, encoding)

    return {"message": "OK"}


@router.post("/upload_binary_file/", description="Загрузка бинарного файла(картинки и др)")
async def upload_binary_file(file: UploadFile):
    logger.debug(f"incoming file attrs: {file.__dict__}")

    write_binary_file(file)

    return {"message": "OK"}


@router.get("/", description="Получение списка всех файлов")
async def get_files():
    files = os.listdir(FILES_FOLDER)
    logger.debug(f"{files=}")

    return {"files": files}
