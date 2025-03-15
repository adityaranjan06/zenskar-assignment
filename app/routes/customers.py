# app/routes/customers.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Customer
from ..schemas import CustomerSchema, CustomerUpdateSchema
from ..kafka_producer import (
    EVENT_CUSTOMER_CREATED,
    EVENT_CUSTOMER_UPDATED,
    EVENT_CUSTOMER_DELETED,
    create_customer_event,
    send_to_kafka
)

router = APIRouter()

@router.get("/customers", response_model=list[CustomerSchema])
def get_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).all()
    return customers

@router.post("/customers", response_model=CustomerSchema, status_code=201)
def create_customer(customer: CustomerSchema, db: Session = Depends(get_db)):
    if db.query(Customer).filter(Customer.id == customer.id).first():
        raise HTTPException(status_code=400, detail="Customer already exists")
    new_customer = Customer(id=customer.id, name=customer.name, email=customer.email)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    event = create_customer_event(EVENT_CUSTOMER_CREATED, new_customer)
    send_to_kafka("customer_events", event)
    return new_customer

@router.get("/customers/{customer_id}", response_model=CustomerSchema)
def get_customer(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/customers/{customer_id}", response_model=CustomerSchema)
def update_customer(customer_id: str, customer: CustomerUpdateSchema, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.id == customer_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Customer not found")
    existing.name = customer.name
    existing.email = customer.email
    db.commit()
    db.refresh(existing)
    event = create_customer_event(EVENT_CUSTOMER_UPDATED, existing)
    send_to_kafka("customer_events", event)
    return existing

@router.delete("/customers/{customer_id}")
def delete_customer(customer_id: str, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.id == customer_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(existing)
    db.commit()
    event = create_customer_event(EVENT_CUSTOMER_DELETED, existing)
    send_to_kafka("customer_events", event)
    return {"detail": "Customer deleted"}
