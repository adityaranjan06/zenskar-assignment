# app/kafka_producer.py
import json
from confluent_kafka import Producer
from .config import KAFKA_BOOTSTRAP_SERVERS

producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})

EVENT_CUSTOMER_CREATED = "customer_created"
EVENT_CUSTOMER_DELETED = "customer_deleted"

def send_to_kafka(topic: str, data: dict):
    message = json.dumps(data).encode("utf-8")
    producer.produce(topic, value=message)
    producer.flush()

def create_customer_event(action: str, customer):
    return {
        "action": action,
        "customer_id": customer.id,
        "customer_name": customer.name,
        "customer_email": customer.email
    }
