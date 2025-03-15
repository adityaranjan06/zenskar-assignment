# Zenskar Assignment

This project implements a two-way integration between a local customer catalog and external systems (Stripe) using FastAPI, SQLite, Kafka (via Docker), and Python.

## Features

- **Customer Catalog API:**  
  CRUD operations on a customer catalog stored in a SQLite database.
- **Stripe Integration:**  
  Two-way synchronization between the local customer catalog and Stripe. When a customer is created, updated or deleted locally, events are sent via Kafka to a worker that updates Stripe. Similarly, Stripe sends webhook events (e.g., `customer.created`, `customer.deleted`, `customer.update`) to update the local catalog.
- **Kafka Integration:**  
  Uses Kafka as a messaging/queuing system to decouple application components.
  
## Setup and Deployment Instructions

### Prerequisites

- **Python 3.8+** installed
- **Docker** installed (for Kafka and Zookeeper)
- **Ngrok**

### Step-by-Step Setup

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/adityaranjan06/zenskar-assignment.git
    cd zenskar-assignment
    ```

2. **Create and Activate a Virtual Environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # For macOS/Linux
    # For Windows: venv\Scripts\activate
    ```

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configure Environment Variables:**

    Create a `.env` file in the project root with the following content (replace placeholder values as needed):

    ```env
    STRIPE_SECRET_KEY="your_stripe_secret_key_here"
    DATABASE_URL="sqlite:///./db.sqlite3"
    KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
    ```

5. **Start Kafka and Zookeeper:**

    Ensure Docker is running and then execute:

    ```bash
    docker-compose up -d
    ```

    *Note:* If the Kafka topic `customer_events` is not auto-created, create it manually:

    ```bash
    docker exec -it fastapi-stripe-kafka-kafka-1 kafka-topics --create --topic customer_events --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1
    ```

6. **Run the FastAPI Application:**

    ```bash
    uvicorn app.main:app --reload
    ```

    The API will be available at [http://localhost:8000](http://localhost:8000) and you can use Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs) to interact with the endpoints.

7. **Run the Kafka Worker:**

    Open a new terminal (with your virtual environment activated) and run:

    ```bash
    python worker/worker.py
    ```

8. **Testing the Application:**

    - **CRUD Operations:**  
      Use Swagger UI ([http://localhost:8000/docs](http://localhost:8000/docs)) or Postman to perform operations on the `/customers` endpoints.
    - **Stripe Webhooks:**  
      Use Ngrok to expose your local server. For example, run:

      ```bash
      ngrok http 8000
      ```

      Then, configure your Stripe test account webhook to point to:

      ```
      https://<ngrok-generated-id>.ngrok-free.app/stripewebhook
      ```

      You can trigger test events from the Stripe Dashboard.

## Extending the Integration

### Plan for Adding a Second Integration with Salesforce's Customer Catalog

To add Salesforce integration, the plan is to create a dedicated module for handling Salesforce API interactions. This module would:

- **Communicate with Salesforce:**  
  Use a library (such as `simple-salesforce`) to authenticate and fetch customer data from Salesforce.
- **Data Transformation:**  
  Map Salesforce customer data into our local customer format (ID, name, email).
- **Event Publication:**  
  Publish customer updates from Salesforce to a dedicated Kafka topic (for example, `salesforce_customer_events`).
- **Dedicated Worker:**  
  Implement a separate worker that listens to this topic and updates the local customer catalog accordingly.

By separating Salesforce events into their own topic and worker, the integration remains isolated from the Stripe integration, allowing both to scale and evolve independently.

### Extending Integrations to Support Other Systems (e.g., Invoice Catalog)

For supporting additional systems such as an invoice catalog, the approach is similar:

- **Modular Design:**  
  Create separate modules for each integration (e.g., one for invoices).
- **Kafka as an Event Bus:**  
  Each integration publishes its events (for instance, invoice creation, updates, deletions) to distinct Kafka topics.
- **Unified Update Mechanism:**  
  Optionally, consolidate events from different systems using Kafka Streams or similar techniques, and update your central product database.
- **Loose Coupling:**  
  Each module operates independently, ensuring that changes in one integration (e.g., Salesforce or Stripe) do not affect the others.

This modular and decoupled architecture makes it straightforward to add new integrations as needed, whether for customers, invoices, or any other catalog.
