from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from services.security.config.database import Base, engine
from services.security.controllers.user import router as user_router
app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CREATE TABLES
Base.metadata.create_all(bind=engine)

app.include_router(user_router, prefix="/api/v1", tags=["users"])

