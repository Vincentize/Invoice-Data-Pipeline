import datetime
import json

import requests

# --- Configuration ---
WEBHOOK_URL = "https://webhook.site/89db4cd6-d72b-40b5-919d-c1b3edd39aff"
CART_URL = "https://fakestoreapi.com/carts/1"
PRODUCT_URL = "https://fakestoreapi.com/products/"


def fetch_order_data(cart_endpoint):
    """Step 1: Ingest the order from the source system."""
    print("Fetching order data...")
    response = requests.get(cart_endpoint, timeout=10)
    response.raise_for_status()
    return response.json()


def _validate_cart(raw_cart):
    """Validate the input contract before building the invoice."""
    required_fields = ["id", "userId", "date", "products"]
    missing_fields = [field for field in required_fields if field not in raw_cart]

    if missing_fields:
        raise ValueError(f"missing required cart fields: {', '.join(missing_fields)}")

    if not isinstance(raw_cart["products"], list):
        raise ValueError("cart products must be a list")

    for item in raw_cart["products"]:
        if "productId" not in item or "quantity" not in item:
            raise ValueError("each cart item must include productId and quantity")


def transform_to_invoice(raw_cart):
    """Step 2: Map and enrich the data into an invoice format."""
    print("Transforming order into invoice...")
    _validate_cart(raw_cart)

    invoice_payload = {
        "invoice_id": f"INV-{raw_cart['id']}-{datetime.date.today().strftime('%Y%m%d')}",
        "customer_id": raw_cart["userId"],
        "order_date": raw_cart["date"],
        "line_items": [],
        "grand_total": 0.0,
        "currency": "EUR",
    }

    for item in raw_cart["products"]:
        product_id = item["productId"]
        quantity = item["quantity"]

        prod_response = requests.get(f"{PRODUCT_URL}{product_id}", timeout=10)
        prod_response.raise_for_status()
        product_data = prod_response.json()

        if "price" not in product_data or "title" not in product_data:
            raise ValueError(f"product {product_id} is missing title or price")

        unit_price = float(product_data["price"])
        line_total = unit_price * quantity

        invoice_payload["line_items"].append(
            {
                "product_id": product_id,
                "description": product_data["title"],
                "quantity": quantity,
                "unit_price": unit_price,
                "line_total": round(line_total, 2),
            }
        )

        invoice_payload["grand_total"] += line_total

    invoice_payload["grand_total"] = round(invoice_payload["grand_total"], 2)
    return invoice_payload


def push_invoice(invoice_data, destination_endpoint):
    """Step 3: Push the formatted invoice to the destination system."""
    print("Pushing invoice to destination system...")
    response = requests.post(destination_endpoint, json=invoice_data, timeout=10)
    response.raise_for_status()
    print("\n--- Success! ---")
    print(f"Invoice {invoice_data['invoice_id']} was successfully delivered.")
    print(f"Destination responded with status code: {response.status_code}")


def main():
    """Main pipeline execution."""
    try:
        raw_order = fetch_order_data(CART_URL)
        final_invoice = transform_to_invoice(raw_order)

        print("\n--- Generated Invoice Payload ---")
        print(json.dumps(final_invoice, indent=4))
        print("---------------------------------\n")

        push_invoice(final_invoice, WEBHOOK_URL)

    except requests.exceptions.RequestException as e:
        print(f"\n[!] Network Error: The pipeline failed to connect to an endpoint. Details: {e}")
    except (KeyError, ValueError) as e:
        print(f"\n[!] Data Validation Error: {e}")
    except Exception as e:
        print(f"\n[!] Unexpected Error: {e}")


if __name__ == "__main__":
    main()