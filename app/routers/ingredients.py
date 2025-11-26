# app/routers/ingredients.py
import csv
import os
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Ingredient

router = APIRouter(
    prefix="/ingredients",
    tags=["ingredients"]
)

