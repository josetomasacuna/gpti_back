from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Preferences, Recipe, User

router = APIRouter(
    prefix="/preferences",
    tags=["preferences"]
)


def get_or_create_preferences(user_id: int, db: Session):
    print(f"[DEBUG] get_or_create_preferences → buscando prefs para user_id={user_id}")
    prefs = db.query(Preferences).filter(Preferences.user_id == user_id).first()
    print(f"[DEBUG] Resultado prefs antes de crear: {prefs}")

    if not prefs:
        print(f"[DEBUG] No existían prefs, creando nuevas...")
        prefs = Preferences(user_id=user_id, positive=[], negative=[])
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
        print(f"[DEBUG] Prefs creadas: {prefs}")

    return prefs


# ---------------------------------------------------------
# 1) Agregar preferencia POSITIVA
# ---------------------------------------------------------
@router.post("/add_positive")
def add_positive(
    user_id: int,
    recipe_id: int,
    db: Session = Depends(get_db)
):
    print(f"\n[DEBUG] add_positive → user_id={user_id}, recipe_id={recipe_id}")

    user = db.query(User).filter(User.id == user_id).first()
    print(f"[DEBUG] Usuario encontrado: {user}")

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no existe.")

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    print(f"[DEBUG] Receta encontrada: {recipe}")

    if not recipe:
        raise HTTPException(status_code=404, detail="Receta no existe.")

    prefs = get_or_create_preferences(user_id, db)
    print(f"[DEBUG] Prefs actuales: positive={prefs.positive}, negative={prefs.negative}")

    if recipe_id not in prefs.positive:
        print(f"[DEBUG] Añadiendo {recipe_id} a positive")
        prefs.positive.append(recipe_id)

    if recipe_id in prefs.negative:
        print(f"[DEBUG] {recipe_id} estaba en negative → removiendo")
        prefs.negative.remove(recipe_id)

    print(f"[DEBUG] Prefs antes de commit: positive={prefs.positive}, negative={prefs.negative}")

    db.commit()
    db.refresh(prefs)

    print(f"[DEBUG] Prefs DESPUÉS del commit: positive={prefs.positive}, negative={prefs.negative}")

    return {"message": "Preferencia positiva agregada."}


# ---------------------------------------------------------
# 2) Agregar preferencia NEGATIVA
# ---------------------------------------------------------
@router.post("/add_negative")
def add_negative(
    user_id: int,
    recipe_id: int,
    db: Session = Depends(get_db)
):
    print(f"\n[DEBUG] add_negative → user_id={user_id}, recipe_id={recipe_id}")

    user = db.query(User).filter(User.id == user_id).first()
    print(f"[DEBUG] Usuario encontrado: {user}")

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no existe.")

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    print(f"[DEBUG] Receta encontrada: {recipe}")

    if not recipe:
        raise HTTPException(status_code=404, detail="Receta no existe.")

    prefs = get_or_create_preferences(user_id, db)
    print(f"[DEBUG] Prefs actuales: positive={prefs.positive}, negative={prefs.negative}")

    if recipe_id not in prefs.negative:
        print(f"[DEBUG] Añadiendo {recipe_id} a negative")
        prefs.negative.append(recipe_id)

    if recipe_id in prefs.positive:
        print(f"[DEBUG] {recipe_id} estaba en positive → removiendo")
        prefs.positive.remove(recipe_id)

    print(f"[DEBUG] Prefs antes de commit: positive={prefs.positive}, negative={prefs.negative}")

    db.commit()
    db.refresh(prefs)

    print(f"[DEBUG] Prefs DESPUÉS del commit: positive={prefs.positive}, negative={prefs.negative}")

    return {"message": "Preferencia negativa agregada."}


# ---------------------------------------------------------
# 3) Obtener preferencias (convertir recipe IDs → nombres)
# ---------------------------------------------------------
@router.get("/get")
def get_preferences(
    user_id: int,
    db: Session = Depends(get_db)
):
    print(f"\n[DEBUG] get_preferences → user_id={user_id}")

    prefs = get_or_create_preferences(user_id, db)
    print(f"[DEBUG] Prefs cargadas: positive={prefs.positive}, negative={prefs.negative}")

    positive_recipes = []
    negative_recipes = []

    if prefs.positive:
        pos_objs = db.query(Recipe).filter(Recipe.id.in_(prefs.positive)).all()
        print(f"[DEBUG] Recetas POS cargadas desde DB: {pos_objs}")
        positive_recipes = [r.name for r in pos_objs]

    if prefs.negative:
        neg_objs = db.query(Recipe).filter(Recipe.id.in_(prefs.negative)).all()
        print(f"[DEBUG] Recetas NEG cargadas desde DB: {neg_objs}")
        negative_recipes = [r.name for r in neg_objs]

    print(f"[DEBUG] Retornando → positive={positive_recipes}, negative={negative_recipes}")

    return {
        "positive": positive_recipes,
        "negative": negative_recipes
    }
