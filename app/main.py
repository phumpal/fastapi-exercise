#!/usr/bin/env python

from fastapi import FastAPI
from app.middleware import RequestLoggingMiddleware
from app.database import init_db
from app.routers import items
from app.logging import logger, log_endpoint

init_db()

app = FastAPI(title="Simple API to manage a list of items")

app.add_middleware(RequestLoggingMiddleware)

app.include_router(items.router)

@app.get("/health")
@log_endpoint("health_check")
def health_check():
    return {"status": "healthy"}
