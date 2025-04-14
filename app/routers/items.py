from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import ItemDB
from app.schemas import Item, ItemCreate
from app.dependencies import get_db
from app.logging import logger, log_endpoint

router = APIRouter(
    prefix="/items",
    tags=["items"],
)

@router.post("/", response_model=Item)
@log_endpoint("create_item")
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = ItemDB(content=item.content)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    logger.info("item_created", item_id=db_item.id, content_length=len(item.content))
    return db_item

@router.get("/", response_model=List[Item])
@log_endpoint("list_items")
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = db.query(ItemDB).offset(skip).limit(limit).all()
    return items
