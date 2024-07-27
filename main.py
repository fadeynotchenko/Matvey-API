import asyncio
import logging
import os
import subprocess
import tempfile
import pymongo
from colorlog import ColoredFormatter
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from motor.motor_asyncio import AsyncIOMotorClient
from cache import CacheManager
from config import url, tls_ca_file, db_client
from latex_helper import generate_latex

# Инициализация FastAPI
app = FastAPI()

# Настройка логирования
# Создание форматера
formatter = ColoredFormatter(
    "%(log_color)s%(levelname)s:%(name)s:%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

# Создание обработчика логов
handler = logging.StreamHandler()
handler.setFormatter(formatter)

# Настройка корневого логгера
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Инициализация менеджера кэша
cache_manager = CacheManager(ttl=30*60)

# Создание асинхронного клиента
client = AsyncIOMotorClient(
    url,
    tls=True,
    tlsCAFile=tls_ca_file
)

db = client[db_client]


@app.get("/{collection_name}")
async def get_documents(collection_name: str):
    sort_field = 'date' if collection_name == "posts" else 'dateStart'
    sort_order = pymongo.DESCENDING if collection_name == "posts" else pymongo.ASCENDING

    cache_key = f"{collection_name}_cache"
    cached_data = cache_manager.get_cached_data(cache_key)

    if cached_data:
        logging.info("Returning cached data for key: %s", cache_key)
        return JSONResponse(content=cached_data)

    # Если данных нет в кэше, загружаем из базы данных
    documents = []
    async for doc in db[collection_name].find().sort(sort_field, sort_order):
        doc['_id'] = str(doc['_id'])
        documents.append(doc)

    logging.info("Caching new data for key: %s", cache_key)
    cache_manager.set_cache_data(cache_key, documents)  # Кэширование результата
    return JSONResponse(content=documents)


async def generate_and_compile_pdf(latex_content: str) -> str:
    tex_filename = ""
    try:
        # Создание временного файла .tex
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tex', mode='w+', encoding='utf-8') as temp_file:
            temp_file.write(latex_content)
            temp_file.flush()
            tex_filename = temp_file.name

        # Определение имен для выходных файлов
        pdf_filename = tex_filename.replace('.tex', '.pdf')
        log_filename = tex_filename.replace('.tex', '.log')

        # Запуск pdflatex для компиляции
        result = subprocess.run(
            ['pdflatex', '-output-directory', os.path.dirname(pdf_filename), tex_filename],
            capture_output=True, text=True
        )

        if result.returncode != 0:
            # Краткое логирование ошибок компиляции
            logging.error("Compilation failed. Check the log file for details.")
            logging.error("Error output: %s", result.stderr.strip())

            # Проверка и удаление лог-файла
            if os.path.exists(log_filename):
                with open(log_filename, 'r', encoding='utf-8') as log_file:
                    log_content = log_file.read().strip()
                logging.error("Log file content:\n%s", log_content)

            # Удаление временных файлов
            os.unlink(tex_filename)
            if os.path.exists(log_filename):
                os.unlink(log_filename)

            # Исключение с краткой ошибкой
            raise RuntimeError(
                "Failed to compile LaTeX file. Please check the logs for details."
            )

        # Удаление лог-файла после успешной компиляции
        if os.path.exists(log_filename):
            os.unlink(log_filename)

        return pdf_filename

    except Exception as e:
        logging.error("Error occurred: %s", str(e))
        raise


@app.post("/generate_pdf")
async def generate_pdf(request: Request):
    data = await request.json()

    try:
        latex_content = generate_latex(data)
        logging.info("LaTeX content generated.")
    except Exception as e:
        logging.error("Error generating LaTeX content: %s", e)
        raise HTTPException(status_code=500, detail=f'Failed to generate LaTeX content: {e}')

    try:
        pdf_filename = await asyncio.get_event_loop().run_in_executor(None, generate_and_compile_pdf, latex_content)
    except Exception as e:
        logging.error("Error generating PDF: %s", e)
        raise HTTPException(status_code=500, detail=f'Failed to generate PDF: {e}')

    return FileResponse(pdf_filename, filename="document.pdf", media_type='application/pdf')


async def refresh_cache():
    while True:
        await cache_manager.refresh_cache(db, ['posts', 'events', 'posts'])
        await asyncio.sleep(cache_manager.ttl)


async def main():
    # Запускаем задачу обновления кэша
    asyncio.create_task(refresh_cache())

    # Запускаем сервер  daksmsakld
    import uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == '__main__':
    asyncio.run(main())  # Запускаем главный асинхронный метод
