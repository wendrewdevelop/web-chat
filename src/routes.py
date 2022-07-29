from fastapi import APIRouter
from src.resource import *


# routes
router = APIRouter()
router.include_router(chat_router)