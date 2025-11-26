import csv
import os
import json
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, Tag, Recipe, Ingredient

router = APIRouter(
    prefix="/data-load",
    tags=["data-load"]
)

@router.post("/load-data")
def load_users():

    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_users_path = os.path.join(base_dir, "users_demo.csv")

    if not os.path.exists(csv_users_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="users_demo.csv not found"
        )

    db: Session = SessionLocal()

    with open(csv_users_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            email = row[0]
            password = row[1]

            user = User(email=email, password=password)
            db.add(user)

        db.commit()

    csv_tags_path = os.path.join(os.path.dirname(__file__), "tags_demo.csv")

    if not os.path.exists(csv_tags_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="tags_demo.csv not found"
        )

    with open(csv_tags_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
        
            existing = db.query(Tag).filter_by(label=row["label"]).first()
            if existing:
                continue

            tag = Tag(
                id=int(row["id"]),
                label=row["label"],
                related_ids=row.get("related_ids", "")
            )
            db.add(tag)

        db.commit()


    json_recipes_path = os.path.join(os.path.dirname(__file__), "recipes.json")

    if not os.path.exists(json_recipes_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="recipes_demo.json not found"
        )

    with open(json_recipes_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    db.query(Recipe).delete()
    db.commit()

    for item in data:
        recipe = Recipe(
            name=item["name"],
            tags=item["tags"],
            ingredients_text=item["ingredients_text"],
            ingredients_ids=item["ingredients_ids"],
            recipe=item["recipe"]
        )
        db.add(recipe)

    db.commit()

    csv_ingredients_path = os.path.join(os.path.dirname(__file__), "ingredients_demo.csv")

    if not os.path.exists(csv_ingredients_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ingredients_demo.csv not found"
        )

    with open(csv_ingredients_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            
            existing = db.query(Ingredient).filter_by(name=row["name"]).first()
            if existing:
                continue

            ingredient = Ingredient(
                id=int(row["id"]),
                name=row["name"],
                category=row["category"],
                unit=row["unit"],
                recommendation=row["recommendation"]
            )
            db.add(ingredient)

        db.commit()


    return {"detail": "Carga completada"}

    
    

    
    


