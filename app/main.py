# app/main.py
from fastapi import FastAPI
from .database import Base, engine
from .routes import customers, webhook

# Create all tables (if not exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Customer Catalog API")

# Include Routers
app.include_router(customers.router)
app.include_router(webhook.router)
