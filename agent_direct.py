import os
import json
import sqlite3
from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
print("Key loaded:", api_key[:10] if api_key else "NOT FOUND")

client = Anthropic(api_key=api_key)

def lookup_customer(customer_id: str) -> dict:
    """The actual tool function -- now querying a real local database instead of a dict."""
    conn = sqlite3.connect("customers.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name, account_status, balance FROM customers WHERE customer_id = ?",
        (customer_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return {"error": f"No customer found with ID {customer_id}"}

    name, account_status, balance = row
    return {"name": name, "account_status": account_status, "balance": balance}

# --- Tool definition Claude sees, describing the function above ---
tools = [
    {
        "name": "lookup_customer",
        "description": "Look up a bank customer's record by their customer ID. Returns name, account status, and balance.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The customer ID to look up, e.g. 'C001'",
                }
            },
            "required": ["customer_id"],
        },
    }
]

def run_agent(user_message: str):
    messages = [{"role": "user", "content": user_message}]

    response = client.messages.create(  # type: ignore
        model="claude-haiku-4-5",
        max_tokens=1024,
        tools=tools,  # type: ignore
        messages=messages,  # type: ignore
    )

    print("Stop reason:", response.stop_reason)
    print("Content blocks:", response.content)

    # Keep looping while Claude wants to use a tool
    while response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})  # type: ignore
        print("--- Looping again ---")
        tool_results = []
        for block in response.content:
            if block.type == "tool_use" and block.name == "lookup_customer":
                result = lookup_customer(**block.input)  # type: ignore
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })

        messages.append({"role": "user", "content": tool_results})  # type: ignore

        response = client.messages.create(  # type: ignore
            model="claude-haiku-4-5",
            max_tokens=1024,
            tools=tools,  # type: ignore
            messages=messages,  # type: ignore
        )

    # Print final text response
    for block in response.content:
        if block.type == "text":
            print(block.text)

if __name__ == "__main__":
    run_agent("Tell me the balance of customer C001 and C003, and also check if C099 exists.")