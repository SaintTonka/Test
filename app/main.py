from fastapi import FastAPI
from app.database import create_all_async, engine
from app.views import router
import logging
from contextlib import asynccontextmanager

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("__name__")

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the app...")
    await create_all_async(engine)
    yield
    logger.info("Shutting down the app...")

app = FastAPI(lifespan=lifespan)

app.include_router(router)
