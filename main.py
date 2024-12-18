from fastapi import FastAPI
from src.endpoints import scraping, inference

app = FastAPI()
app.include_router(scraping.router)
app.include_router(inference.router)
