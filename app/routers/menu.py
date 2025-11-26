from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import random
from app.database import get_db
from app.models import Recipe, Tag, Menu, ShoppingList, User, Ingredient
import random


router = APIRouter(
    prefix="/menus",
    tags=["menus"]
)

@router.post("/create")
def create_menu(
    user_id: int,
    tag_ids: list[int] = Query(...),
    db: Session = Depends(get_db)
):
    
    validate_user_exists(user_id, db)

    recipe_ids = select_recipes_for_menu(tag_ids, db)

    menu = Menu(user_id=user_id, recipe_ids=recipe_ids)
    db.add(menu)
    db.commit()
    db.refresh(menu)

    shopping_items = generate_shopping_list(db, recipe_ids)

    shopping_list = ShoppingList(id=menu.id, items=shopping_items)
    db.add(shopping_list)
    db.commit()
    
    recipes = (
        db.query(Recipe)
        .filter(Recipe.id.in_(recipe_ids))
        .all()
    )

    all_tag_ids = {tag_id for r in recipes for tag_id in r.tags}

    tag_map = {
        t.id: t.label
        for t in db.query(Tag).filter(Tag.id.in_(all_tag_ids)).all()
    }

    recipes_serialized = [
        {
            "id": r.id,
            "name": r.name,
            "tags": [tag_map[tag_id] for tag_id in r.tags],
            "ingredients_text": r.ingredients_text,
            "ingredients_ids": r.ingredients_ids,
            "recipe": r.recipe
        }
        for r in recipes
    ]

    return {
        "menu_id": menu.id,
        "user_id": user_id,
        "recipes": recipes_serialized,
        "shopping_list": shopping_items   
    }


def validate_user_exists(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
def select_recipes_for_menu(tag_ids: list[int], db: Session) -> list[int]:
    filtered_recipes = db.query(Recipe).filter(
        Recipe.tags.op("&&")(tag_ids)  
    ).all()

    total_needed = 15
    selected = filtered_recipes.copy()

    if len(selected) < total_needed:
        selected_ids = [r.id for r in selected]
        remaining = db.query(Recipe).filter(~Recipe.id.in_(selected_ids)).all()
        n_missing = total_needed - len(selected)
        if remaining:  
            selected += random.sample(remaining, min(n_missing, len(remaining)))

    if len(selected) > total_needed:
        selected = random.sample(selected, total_needed)

    return [r.id for r in selected]

def generate_shopping_list(db: Session, recipe_ids: list[int]) -> list[dict]:
    recipes = (
        db.query(Recipe)
        .filter(Recipe.id.in_(recipe_ids))
        .all()
    )

    shopping_dict = {}

    for r in recipes:
        for item in r.ingredients_ids:
            ingredient = db.query(Ingredient).filter(Ingredient.id == item["id"]).first()
            unit = ingredient.unit
            name = ingredient.name
            quantity = item["quantity"]
            recommendation = ingredient.recommendation

            if name in shopping_dict:
                shopping_dict[name]["quantity"] += quantity
                
            else:
                shopping_dict[name] = {
                    "name": name,
                    "unit": unit,
                    "quantity": quantity,
                    "recomendation": recommendation
                }

    return list(shopping_dict.values())

@router.get("/menu_history")
def get_menu_history(
    user_id: int,
    db: Session = Depends(get_db)
):
    validate_user_exists(user_id, db)

    menus = (
        db.query(Menu)
        .filter(Menu.user_id == user_id)
        .order_by(Menu.created_at.desc())
        .all()
    )

    history = []

    for menu in menus:
        # Buscar shopping list asociada al menú
        shopping_list = (
            db.query(ShoppingList)
            .filter(ShoppingList.id == menu.id)
            .first()
        )
        
        # Obtener las recetas completas del menú
        recipes = (
            db.query(Recipe)
            .filter(Recipe.id.in_(menu.recipe_ids))
            .all()
        )

        recipe_objects = []

        # Construcción del objeto receta personalizado
        for r in recipes:
            # Obtener labels de los tags
            tag_labels = []
            if r.tags:
                tags = (
                    db.query(Tag)
                    .filter(Tag.id.in_(r.tags))
                    .all()
                )
                tag_labels = [t.label for t in tags]

            recipe_objects.append({
                "id": r.id,
                "name": r.name,
                "tags": tag_labels,
                "ingredients_text": r.ingredients_text,
                "ingredients_ids": r.ingredients_ids,
                "recipe": r.recipe
            })

        history.append({
            "menu_id": menu.id,
            "created_at": menu.created_at,
            "recipes": recipe_objects,
            "shopping_list": shopping_list.items if shopping_list else []
        })

    return history
