#!/usr/bin/env python
import os
import time
import uuid

from typing import Union, List
from fastapi import FastAPI, Depends, HTTPException, Request, Response

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.engine.url import URL

from pydantic import BaseModel

import structlog
from starlette.middleware.base import BaseHTTPMiddleware

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DATABASE_URL = str(URL.create(
        drivername="postgresql",
        username=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        database=os.getenv("POSTGRES_DB"),
    ))

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ItemDB(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)

Base.metadata.create_all(bind=engine)

class ItemBase(BaseModel):
    content: str

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    model_config = {"from_attributes": True}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        request.state.start_time = time.time()

        logger.info(
            "request_started",
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host,
        )

        try:
            response = await call_next(request)

            logger.info(
                "request_completed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round((time.time() - request.state.start_time) * 1000, 2),
            )

            return response
        except Exception as e:
            logger.error(
                "request_failed",
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_ms=round((time.time() - request.state.start_time) * 1000, 2),
            )
            raise

app = FastAPI()
app.add_middleware(LoggingMiddleware)

@app.get("/")
def read_root():
    logger.info("root_endpoint_called")
    return {"Hello": "World"}

@app.post("/items/", response_model=Item)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    try:
        db_item = ItemDB(content=item.content)
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        logger.info("item_created", item_id=db_item.id, content_length=len(item.content))
        return db_item
    except Exception as e:
        logger.error("item_creation_failed", error=str(e))
        raise

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    logger.info("item_requested", item_id=item_id)
    db_item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if db_item is None:
        logger.warning("item_not_found", item_id=item_id)
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.get("/items/", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    logger.info("items_list_requested", skip=skip, limit=limit)
    items = db.query(ItemDB).offset(skip).limit(limit).all()
    logger.info("items_list_returned", count=len(items))
    return items

@app.get("/health")
def health_check():
    logger.info("health_check_performed")
    return {"status": "healthy"}
