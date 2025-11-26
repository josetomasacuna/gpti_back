# app/routers/recipes.py
import json
import os
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Recipe, Tag
import random


router = APIRouter(
    prefix="/recipes",
    tags=["recipes"]
)


@router.get("/select-by-tags")
def select_recipes_by_tags(tag_ids: list[int] = Query(...), db: Session = Depends(get_db)):
    # Filtrar recetas que tengan al menos un tag de la lista usando PostgreSQL
    filtered_recipes = db.query(Recipe).filter(
        Recipe.tags.op("&&")(tag_ids)  # operador "overlap" de Postgres para arrays
    ).all()

    total_needed = 15
    selected = filtered_recipes.copy()

    # Completar con aleatorio si hay menos de 15
    if len(selected) < total_needed:
        selected_ids = [r.id for r in selected]
        remaining = db.query(Recipe).filter(~Recipe.id.in_(selected_ids)).all()
        n_missing = total_needed - len(selected)
        if remaining:  
            selected += random.sample(remaining, min(n_missing, len(remaining)))

    # Recortar aleatoriamente si hay más de 15
    if len(selected) > total_needed:
        selected = random.sample(selected, total_needed)

    # Convertir a lista de dicts y reemplazar tags por nombres
    result = []
    for r in selected:
        # Obtener nombres de tags
        tag_labels = [
            db.query(Tag.label).filter(Tag.id == tag_id).scalar()
            for tag_id in r.tags
        ]
        result.append({
            "name": r.name,
            "tags": tag_labels,  # ahora solo los nombres
            "ingredients_text": r.ingredients_text,
            "ingredients_ids": r.ingredients_ids,
            "recipe": r.recipe
        })

    return result


