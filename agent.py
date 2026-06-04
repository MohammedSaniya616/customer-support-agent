import json
import os
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic

# LOAD ENV VARIABLES

load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")

print("API KEY:", api_key)

client = Anthropic(
    api_key=api_key
)

# LOAD DATASET

with open("support-tickets.json", "r") as f:
    data = json.load(f)

# TOOL 1 - GET CUSTOMER

def get_customer(name):

    for customer in data["customers"]:

        if customer["name"].lower() == name.lower():

            return {
                "status": "success",
                "customer_id": customer["customer_id"],
                "verified": customer["verified"]
            }

    return {
        "status": "error",
        "category": "validation",
        "isRetryable": False,
        "message": "Customer not found"
    }

# TOOL 2 - LOOKUP ORDER

def lookup_order(customer_id):

    customer_orders = []

    for order in data["orders"]:

        if order["customer_id"] == customer_id:

            customer_orders.append(order)

    return {
        "status": "success",
        "orders": customer_orders
    }

# TOOL 3 - PROCESS REFUND

def process_refund(order_id, amount):

    return {
        "status": "success",
        "refund_id": "R10001",
        "amount": amount,
        "message": "Refund processed successfully"
    }

# TOOL 4 - ESCALATE TO HUMAN

def escalate_to_human(summary):

    return {
        "status": "escalated",
        "message": "Case sent to human support",
        "summary": summary
    }

# TOOL DEFINITIONS FOR CLAUDE

tools = [

    {
        "name": "get_customer",

        "description": "Verify customer identity using customer name",

        "input_schema": {
            "type": "object",

            "properties": {
                "name": {
                    "type": "string"
                }
            },

            "required": ["name"]
        }
    },

    {
        "name": "lookup_order",

        "description": "Look up orders for verified customer",

        "input_schema": {
            "type": "object",

            "properties": {
                "customer_id": {
                    "type": "string"
                }
            },

            "required": ["customer_id"]
        }
    },

    {
        "name": "process_refund",

        "description": "Process refund for an order",

        "input_schema": {
            "type": "object",

            "properties": {

                "order_id": {
                    "type": "string"
                },

                "amount": {
                    "type": "number"
                }
            },

            "required": ["order_id", "amount"]
        }
    },

    {
        "name": "escalate_to_human",

        "description": "Escalate issue to human support",

        "input_schema": {
            "type": "object",

            "properties": {
                "summary": {
                    "type": "string"
                }
            },

            "required": ["summary"]
        }
    }
]

# SYSTEM PROMPT

SYSTEM_PROMPT = """
You are a customer support AI agent.

Rules:
1. Always verify customer before refunds
2. Never refund above $500 automatically
3. If customer owns multiple similar products, ask clarification
4. Use tools carefully
5. Escalate risky cases
"""

# USER MESSAGE

messages = [
    {
        "role": "user",
        "content": "Hi, it's Asha. My water heater is faulty, I want a refund."
    }
]

# VERIFIED CUSTOMER CHECK

verified_customer = None

# AGENTIC LOOP

print("\nCUSTOMER MESSAGE:")
print("Hi, it's Asha. My water heater is faulty, I want a refund.")

# STEP 1 — VERIFY CUSTOMER

customer_result = get_customer("Asha")

print("\nSTEP 1 — CUSTOMER VERIFICATION:")
print(customer_result)

# STEP 2 — LOOKUP ORDERS

orders_result = lookup_order(customer_result["customer_id"])

print("\nSTEP 2 — CUSTOMER ORDERS:")
print(orders_result)

# STEP 3 — FIND WATER HEATERS

print("\nSTEP 3 — MULTIPLE WATER HEATERS FOUND")

water_heaters = []

for order in orders_result["orders"]:

    if order["product"] == "Water Heater":

        water_heaters.append(order)

        print(
            f"""
Order ID: {order['order_id']}
Brand: {order['brand']}
Price: ${order['price']}
Purchase Date: {order['purchase_date']}
"""
        )

# STEP 4 — SELECT ONE ORDER

selected_order = orders_result["orders"][3]

print("\nSTEP 4 — SELECTED ORDER:")
print(selected_order)

# STEP 5 — REFUND CHECK

amount = selected_order["price"]

if amount > 500:

    summary = f"""
Customer ID: {customer_result['customer_id']}
Issue: High refund amount
Amount: ${amount}
Recommendation: Escalate
"""

    escalation = escalate_to_human(summary)

    print("\nSTEP 5 — ESCALATION:")

    print(f"""
    ======== HUMAN ESCALATION SUMMARY ========

    Customer ID: {customer_result['customer_id']}

    Issue:
    High refund amount request

    Order ID:
    {selected_order['order_id']}

    Amount:
    ${amount}

    Recommended Action:
    Manual human review required

    ==========================================
    """)

else:

    refund = process_refund(
        selected_order["order_id"],
        amount
    )

    print("\nSTEP 5 — REFUND SUCCESS:")
    print(refund)

print("\nPROJECT COMPLETED SUCCESSFULLY")