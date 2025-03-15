# app/routes/webhook.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Customer
from ..schemas import StripeWebhookEvent

router = APIRouter()

@router.post("/stripewebhook")
async def stripe_webhook(event: StripeWebhookEvent, db: Session = Depends(get_db)):
    print("Received Stripe webhook event:", event)
    event_type = event.type
    customer_data = event.data.object

    if event_type == "customer.created":
        customer_id = customer_data.get("id")
        customer_name = customer_data.get("name")
        customer_email = customer_data.get("email")
        if not db.query(Customer).filter(Customer.id == customer_id).first():
            new_customer = Customer(id=customer_id, name=customer_name, email=customer_email)
            db.add(new_customer)
            db.commit()
            db.refresh(new_customer)
            print(f"Created customer with id={customer_id}")
        else:
            print(f"Customer with id={customer_id} already exists")
            
    elif event_type == "customer.updated":
        customer_id = customer_data.get("id")
        customer_name = customer_data.get("name")
        customer_email = customer_data.get("email")
        existing = db.query(Customer).filter(Customer.id == customer_id).first()
        if existing:
            existing.name = customer_name
            existing.email = customer_email
            db.commit()
            db.refresh(existing)
            print(f"Updated customer with id={customer_id}")
        else:
            new_customer = Customer(id=customer_id, name=customer_name, email=customer_email)
            db.add(new_customer)
            db.commit()
            db.refresh(new_customer)
            print(f"Created customer with id={customer_id} on update event")
            
    elif event_type == "customer.deleted":
        customer_id = customer_data.get("id")
        existing = db.query(Customer).filter(Customer.id == customer_id).first()
        if existing:
            db.delete(existing)
            db.commit()
            print(f"Deleted customer with id={customer_id}")
        else:
            print(f"Customer with id={customer_id} does not exist")
            
    else:
        print(f"Unhandled event type: {event_type}")
        
    return {"status": "success"}
