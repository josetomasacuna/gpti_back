from .database import Base, engine
from sqlalchemy import Column, Integer, ForeignKey, JSON, DateTime, ARRAY, String
from sqlalchemy.sql import func
from sqlalchemy.ext.mutable import MutableList



class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    category = Column(String, nullable=False)
    unit = Column(String, nullable=False) 
    recommendation = Column(String, nullable=True)

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False, unique=True)
    related_ids = Column(String, nullable=True) 

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    tags = Column(ARRAY(Integer), nullable=False) 
    ingredients_text = Column(JSON, nullable=False)
    ingredients_ids = Column(JSON, nullable=False)
    recipe = Column(JSON, nullable=False)

class Menu(Base):
    __tablename__ = "menus"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recipe_ids = Column(JSON, nullable=False)  
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ShoppingList(Base):
    __tablename__ = "shopping_lists"
    id = Column(Integer, ForeignKey("menus.id"), primary_key=True)  
    items = Column(JSON, nullable=False)  

class Preferences(Base):
    __tablename__ = "preferences"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)

    positive = Column(
        MutableList.as_mutable(JSON), 
        nullable=False, 
        default=list
    )

    negative = Column(
        MutableList.as_mutable(JSON), 
        nullable=False, 
        default=list
    )   
