# worker/worker.py
import json
import stripe
from confluent_kafka import Consumer, KafkaError
from dotenv import load_dotenv
import os

load_dotenv() 

EVENT_CUSTOMER_CREATED = "customer_created"
EVENT_CUSTOMER_UPDATED = "customer_updated" 
EVENT_CUSTOMER_DELETED = "customer_deleted"

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")

consumer = Consumer({
    "bootstrap.servers": os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    "group.id": "fastapi-group",
    "auto.offset.reset": "earliest"
})
consumer.subscribe(["customer_events"])

def process_message(msg):
    try:
        event = json.loads(msg.value().decode("utf-8"))
    except Exception as e:
        print("Error decoding message:", e)
        return

    action = event.get("action")
    customer_id = event.get("customer_id")
    customer_name = event.get("customer_name")
    customer_email = event.get("customer_email")

    if action == EVENT_CUSTOMER_CREATED:
        try:
            stripe.Customer.create(
                id=customer_id,
                name=customer_name,
                email=customer_email
            )
            print(f"Stripe: Customer {customer_id} created.")
        except Exception as e:
            print(f"Stripe: Error creating customer {customer_id}: {e}")

    elif action == EVENT_CUSTOMER_UPDATED:
        try:
            stripe.Customer.modify(
                customer_id,
                name=customer_name,
                email=customer_email
            )
            print(f"Stripe: Customer {customer_id} updated.")
        except Exception as e:
            print(f"Stripe: Error updating customer {customer_id}: {e}")

    elif action == EVENT_CUSTOMER_DELETED:
        try:
            stripe.Customer.delete(customer_id)
            print(f"Stripe: Customer {customer_id} deleted.")
        except stripe.error.InvalidRequestError as e:
            print(f"Stripe: Customer {customer_id} not found in Stripe: {e}")
        except Exception as e:
            print(f"Stripe: Error deleting customer {customer_id}: {e}")
    else:
        print(f"Unknown action {action}")

def main():
    print("Starting Kafka consumer worker...")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    print("End of partition reached")
                else:
                    print("Kafka error:", msg.error())
            else:
                print("Received message:", msg.value())
                process_message(msg)
                consumer.commit()
    except KeyboardInterrupt:
        print("Stopping worker...")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()
