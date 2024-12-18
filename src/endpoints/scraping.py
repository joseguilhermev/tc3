from fastapi import APIRouter
from pydantic import BaseModel
from src.utils import extract_and_insert_features

router = APIRouter()


class ScrapingRequest(BaseModel):
    url: str
    collection_name: str = "prices"


@router.post("/extract", tags=["scraping"])
def extract(request: ScrapingRequest):
    """
    Extracts data from the given URL and appends it to the specified MongoDB collection.
    Returns the result of the extraction process.
    """
    result = extract_and_insert_features(request.url, request.collection_name)
    return result
