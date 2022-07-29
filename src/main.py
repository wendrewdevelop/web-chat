import uvicorn
from imp import reload
from fastapi.middleware.cors import CORSMiddleware
from src.utils.services import app
from src.utils.validators import Validator
from .routes import router as api_router


URL_local = ["http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=URL_local,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="localhost",
        port=8000,
        log_level="info",
        reload=True
    )
    print("running")