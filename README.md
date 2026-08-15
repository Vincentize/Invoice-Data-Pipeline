# Automated Order-to-Invoice Pipeline

A custom Python connector built to automatically map and move order and invoice data between different platforms using REST APIs. 

This project demonstrates core backend integration concepts, including data ingestion, JSON payload transformation, data enrichment, and automated HTTP delivery.

## ⚙️ How It Works

The script acts as a middleware connector executing a three-step ETL (Extract, Transform, Load) pipeline:

1. **Ingest (GET):** Fetches raw, pending shopping cart data from a simulated storefront API.
2. **Transform & Enrich:** Parses the initial JSON payload, makes secondary API calls to look up real-time pricing for each item, and maps the combined data into a structured financial invoice format.
3. **Deliver (POST):** Pushes the final, formatted invoice payload to a destination accounting system/webhook.

## 🛠️ Technologies Used

* **Language:** Python 3
* **Libraries:** `requests`, `json`, `datetime`
* **Concepts:** REST APIs, Data Mapping, Error Handling, JSON Manipulation

## 🚀 Setup & Installation

To run this connector locally, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR-USERNAME/Invoice-Data-Pipeline.git](https://github.com/YOUR-USERNAME/Invoice-Data-Pipeline.git)
   cd Invoice-Data-Pipeline
