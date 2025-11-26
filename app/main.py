from fastapi import FastAPI
from app.routers import auth, menu, recipes, preferences, ingredients, data_load
from .database import Base, engine
from . import models
from app.routers import users_upload
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(preferences.router)

app.include_router(ingredients.router)
app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(recipes.router)
app.include_router(data_load.router)
app.include_router(preferences.router)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "API de recetas funcionando 🎉"}

