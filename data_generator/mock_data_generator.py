import os
import json
import random
from pathlib import Path
import argparse
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from faker import Faker

# ============================================================
# CONFIG
# ============================================================

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
fake = Faker()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

BASE_DATA_DIR = PROJECT_ROOT / "data"
FULL_LOAD_DIR = os.path.join(BASE_DATA_DIR, "full_data")
INCREMENTAL_DIR = os.path.join(BASE_DATA_DIR, "incremental")
MASTER_DIR = os.path.join(BASE_DATA_DIR, "staging")
STATE_FILE = os.path.join(BASE_DATA_DIR, "state.json")

os.makedirs(FULL_LOAD_DIR, exist_ok=True)
os.makedirs(INCREMENTAL_DIR, exist_ok=True)
os.makedirs(MASTER_DIR, exist_ok=True)

# ---------------- FULL LOAD COUNTS ----------------
FULL_N_CUSTOMERS = 5000
FULL_N_SELLERS = 200
FULL_N_PRODUCTS = 10000
FULL_N_ORDERS = 50000

# ---------------- DAILY INCREMENTAL RANGES ----------------
DAILY_NEW_CUSTOMERS = (20, 80)
DAILY_NEW_SELLERS = (0, 3)
DAILY_NEW_PRODUCTS = (5, 20)
DAILY_NEW_ORDERS = (150, 400)

# Order items per order range
MIN_ITEMS_PER_ORDER = 1
MAX_ITEMS_PER_ORDER = 5

# Approx return rate for delivered items
RETURN_RATE = 0.08  # 8%

# ============================================================
# LOOKUP / STATIC DATA
# ============================================================

PH_CITIES = [
    ("Quezon City", "Metro Manila", "Philippines"),
    ("Manila", "Metro Manila", "Philippines"),
    ("Makati", "Metro Manila", "Philippines"),
    ("Taguig", "Metro Manila", "Philippines"),
    ("Pasig", "Metro Manila", "Philippines"),
    ("Cebu City", "Cebu", "Philippines"),
    ("Davao City", "Davao del Sur", "Philippines"),
    ("Iloilo City", "Iloilo", "Philippines"),
    ("Baguio", "Benguet", "Philippines"),
    ("Cagayan de Oro", "Misamis Oriental", "Philippines"),
    ("Bacolod", "Negros Occidental", "Philippines"),
    ("Parañaque", "Metro Manila", "Philippines"),
    ("Las Piñas", "Metro Manila", "Philippines"),
    ("Muntinlupa", "Metro Manila", "Philippines"),
    ("Marikina", "Metro Manila", "Philippines"),
]

SHIPPING_METHODS = ["Standard", "Express", "Same Day"]
PAYMENT_METHODS = ["Credit Card", "Debit Card", "GCash", "PayPal", "Cash on Delivery", "Bank Transfer"]

RETURN_REASONS = [
    "Damaged item",
    "Wrong item",
    "Changed mind",
    "Size issue",
    "Late delivery",
    "Missing parts",
]

SELLER_TYPES = ["Individual", "Business", "Brand"]
CUSTOMER_SEGMENTS = ["New", "Returning", "VIP"]

ORDER_STATUS_WEIGHTS = {
    "placed": 0.05,
    "shipped": 0.10,
    "delivered": 0.70,
    "cancelled": 0.10,
    "returned": 0.05,
}

CATEGORY_DATA = [
    ("Electronics", "Phones", "Electronics"),
    ("Electronics", "Laptops", "Electronics"),
    ("Electronics", "Audio", "Electronics"),
    ("Home & Kitchen", "Cookware", "Home"),
    ("Home & Kitchen", "Furniture", "Home"),
    ("Home & Kitchen", "Storage", "Home"),
    ("Fashion", "Men Clothing", "Fashion"),
    ("Fashion", "Women Clothing", "Fashion"),
    ("Fashion", "Shoes", "Fashion"),
    ("Beauty", "Skincare", "Beauty"),
    ("Beauty", "Makeup", "Beauty"),
    ("Sports", "Fitness", "Sports"),
    ("Sports", "Outdoor", "Sports"),
    ("Toys", "Kids Toys", "Kids"),
    ("Books", "Fiction", "Books"),
    ("Books", "Non-Fiction", "Books"),
    ("Groceries", "Snacks", "Food"),
    ("Groceries", "Beverages", "Food"),
    ("Pet Supplies", "Dog", "Pets"),
    ("Pet Supplies", "Cat", "Pets"),
]

BRANDS_BY_DEPARTMENT = {
    "Electronics": ["Samsung", "Apple", "Sony", "Xiaomi", "Asus", "Acer", "JBL", "Logitech"],
    "Home": ["IKEA", "Tefal", "Oster", "Philips", "Hanabishi", "Dowell"],
    "Fashion": ["Nike", "Adidas", "Uniqlo", "H&M", "Zara", "Penshoppe"],
    "Beauty": ["Maybelline", "L'Oreal", "Cetaphil", "Nivea", "The Ordinary"],
    "Sports": ["Nike", "Adidas", "Puma", "Under Armour", "Decathlon"],
    "Kids": ["Lego", "Fisher-Price", "Mattel", "Hasbro"],
    "Books": ["Penguin", "HarperCollins", "Simon & Schuster", "O'Reilly"],
    "Food": ["Nestle", "Coca-Cola", "Pepsi", "Monde Nissin", "Jack 'n Jill"],
    "Pets": ["Pedigree", "Whiskas", "Royal Canin", "Aozi"],
}

PRODUCT_NAME_TEMPLATES = {
    "Electronics": [
        "Wireless Earbuds", "Bluetooth Speaker", "Gaming Mouse", "Mechanical Keyboard",
        "Smartphone", "Laptop Sleeve", "USB-C Charger", "Portable SSD", "Webcam", "Power Bank",
    ],
    "Home": [
        "Nonstick Pan", "Storage Box", "Dining Chair", "LED Desk Lamp",
        "Air Fryer", "Electric Kettle", "Shoe Rack", "Wardrobe Organizer",
    ],
    "Fashion": [
        "Cotton T-Shirt", "Slim Fit Jeans", "Running Shoes", "Hoodie",
        "Sneakers", "Casual Polo", "Jogger Pants", "Backpack",
    ],
    "Beauty": [
        "Facial Cleanser", "Moisturizer", "Sunscreen", "Lipstick",
        "Serum", "Shampoo", "Conditioner",
    ],
    "Sports": [
        "Yoga Mat", "Resistance Bands", "Dumbbell Set", "Basketball",
        "Cycling Gloves", "Water Bottle",
    ],
    "Kids": [
        "Building Blocks", "Toy Car", "Puzzle Set", "Educational Toy", "Doll House",
    ],
    "Books": [
        "Programming Guide", "Mystery Novel", "Business Book", "Self-Help Book", "Fantasy Novel",
    ],
    "Food": [
        "Chocolate Cookies", "Instant Coffee", "Potato Chips", "Fruit Juice", "Trail Mix",
    ],
    "Pets": [
        "Dog Food", "Cat Litter", "Pet Shampoo", "Dog Leash", "Cat Toy",
    ],
}

CARRIERS = ["LBC", "J&T Express", "Ninja Van", "Flash Express", "DHL eCommerce"]

# ============================================================
# HELPERS
# ============================================================

def weighted_choice(weight_map):
    choices = list(weight_map.keys())
    weights = list(weight_map.values())
    return random.choices(choices, weights=weights, k=1)[0]


def random_date(start_date, end_date):
    delta = end_date - start_date
    random_seconds = random.randint(0, max(1, int(delta.total_seconds())))
    return start_date + timedelta(seconds=random_seconds)


def random_ph_location():
    city, state, country = random.choice(PH_CITIES)
    postal_code = str(random.randint(1000, 9999))
    return city, state, country, postal_code


def generate_email(first_name, last_name, customer_id):
    domain = random.choice(["gmail.com", "yahoo.com", "outlook.com"])
    return f"{first_name.lower()}.{last_name.lower()}{customer_id}@{domain}".replace(" ", "")


def safe_round(value, digits=2):
    return round(float(value), digits)


def get_price_range(department):
    ranges = {
        "Electronics": (500, 50000),
        "Home": (150, 12000),
        "Fashion": (200, 5000),
        "Beauty": (120, 2500),
        "Sports": (250, 15000),
        "Kids": (150, 5000),
        "Books": (100, 1500),
        "Food": (50, 800),
        "Pets": (120, 3500),
    }
    return ranges.get(department, (100, 3000))


def ensure_datetime(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


# ============================================================
# STATE MANAGEMENT
# ============================================================

def default_state():
    return {
        "last_customer_id": 0,
        "last_seller_id": 0,
        "last_product_id": 0,
        "last_order_id": 0,
        "last_order_item_id": 0,
        "last_payment_id": 0,
        "last_event_id": 0,
        "last_return_id": 0,
    }


def load_state():
    if not os.path.exists(STATE_FILE):
        return default_state()
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


# ============================================================
# FILE HELPERS
# ============================================================

def save_csv(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved: {path}")


def append_master(df, filename):
    """
    Append rows to master CSV. If master file doesn't exist, create it.
    """
    path = os.path.join(MASTER_DIR, filename)
    if os.path.exists(path):
        existing = pd.read_csv(path)
        combined = pd.concat([existing, df], ignore_index=True)
        combined.to_csv(path, index=False)
    else:
        df.to_csv(path, index=False)
    print(f"Updated master: {path}")


def write_master(df, filename):
    path = os.path.join(MASTER_DIR, filename)
    save_csv(df, path)


def read_master(filename):
    path = os.path.join(MASTER_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing master file: {path}")
    return pd.read_csv(path)


# ============================================================
# GENERATORS
# ============================================================

def generate_product_categories():
    rows = []
    for i, (category_name, parent_category, department) in enumerate(CATEGORY_DATA, start=1):
        rows.append({
            "category_id": i,
            "category_name": category_name,
            "parent_category": parent_category,
            "department": department
        })
    return pd.DataFrame(rows)


def generate_customers(n_customers, start_customer_id, batch_date):
    rows = []

    # if batch_date == "full_load", spread across history
    # otherwise keep signup_date around the batch date
    if batch_date == "full_load":
        start_signup = datetime(2022, 1, 1)
        end_signup = datetime(2025, 12, 31)
    else:
        batch_dt = pd.to_datetime(batch_date)
        start_signup = batch_dt
        end_signup = batch_dt + timedelta(hours=23, minutes=59, seconds=59)

    for customer_id in range(start_customer_id, start_customer_id + n_customers):
        first_name = fake.first_name()
        last_name = fake.last_name()
        city, state, country, postal_code = random_ph_location()

        signup_dt = random_date(start_signup, end_signup)

        rows.append({
            "customer_id": customer_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": generate_email(first_name, last_name, customer_id),
            "phone": "63" + fake.msisdn()[:10],
            "signup_date": signup_dt.date(),
            "city": city,
            "state": state,
            "country": country,
            "postal_code": postal_code,
            "customer_segment": random.choices(CUSTOMER_SEGMENTS, weights=[0.45, 0.45, 0.10], k=1)[0],
            "batch_date": batch_date
        })

    return pd.DataFrame(rows)


def generate_sellers(n_sellers, start_seller_id, batch_date):
    rows = []

    if batch_date == "full_load":
        start_join = datetime(2021, 1, 1)
        end_join = datetime(2025, 12, 31)
    else:
        batch_dt = pd.to_datetime(batch_date)
        start_join = batch_dt
        end_join = batch_dt + timedelta(hours=23, minutes=59, seconds=59)

    for seller_id in range(start_seller_id, start_seller_id + n_sellers):
        city, state, country, _ = random_ph_location()
        seller_type = random.choices(SELLER_TYPES, weights=[0.35, 0.45, 0.20], k=1)[0]

        if seller_type == "Individual":
            seller_name = f"{fake.last_name()} Store"
        elif seller_type == "Business":
            seller_name = f"{fake.company()} Trading"
        else:
            seller_name = f"{fake.company()} Official"

        rows.append({
            "seller_id": seller_id,
            "seller_name": seller_name[:80],
            "seller_type": seller_type,
            "seller_city": city,
            "seller_state": state,
            "seller_country": country,
            "join_date": random_date(start_join, end_join).date(),
            "rating": safe_round(np.clip(np.random.normal(4.3, 0.4), 2.5, 5.0), 2),
            "batch_date": batch_date
        })

    return pd.DataFrame(rows)


def generate_products(n_products, start_product_id, categories_df, sellers_df, batch_date):
    rows = []
    seller_ids = sellers_df["seller_id"].tolist()

    if batch_date == "full_load":
        created_start = datetime(2022, 1, 1)
        created_end = datetime(2025, 12, 31)
    else:
        batch_dt = pd.to_datetime(batch_date)
        created_start = batch_dt
        created_end = batch_dt + timedelta(hours=23, minutes=59, seconds=59)

    for product_id in range(start_product_id, start_product_id + n_products):
        category = categories_df.sample(1).iloc[0]
        category_id = int(category["category_id"])
        department = category["department"]

        seller_id = random.choice(seller_ids)
        brand = random.choice(BRANDS_BY_DEPARTMENT.get(department, ["Generic"]))
        base_name = random.choice(PRODUCT_NAME_TEMPLATES.get(department, ["Product"]))
        variant = random.choice(["Standard", "Pro", "Mini", "Max", "Lite", "Plus"])
        product_name = f"{brand} {base_name} {variant}"

        min_price, max_price = get_price_range(department)
        price = safe_round(np.random.uniform(min_price, max_price), 2)
        cost = safe_round(price * np.random.uniform(0.45, 0.8), 2)

        created_at = random_date(created_start, created_end)

        rows.append({
            "product_id": product_id,
            "product_name": product_name[:120],
            "category_id": category_id,
            "seller_id": seller_id,
            "brand": brand,
            "sku": f"SKU-{department[:3].upper()}-{product_id:06d}",
            "price": price,
            "cost": cost,
            "stock_quantity": random.randint(0, 500),
            "created_at": created_at,
            "is_active": random.choices([True, False], weights=[0.92, 0.08], k=1)[0],
            "batch_date": batch_date
        })

    return pd.DataFrame(rows)


def generate_orders(n_orders, start_order_id, customers_df, batch_date):
    rows = []
    customer_ids = customers_df["customer_id"].tolist()

    if batch_date == "full_load":
        order_start = datetime(2023, 1, 1)
        order_end = datetime(2025, 12, 31, 23, 59, 59)
    else:
        batch_dt = pd.to_datetime(batch_date)
        order_start = batch_dt
        order_end = batch_dt + timedelta(hours=23, minutes=59, seconds=59)

    for order_id in range(start_order_id, start_order_id + n_orders):
        customer_id = random.choice(customer_ids)
        order_date = random_date(order_start, order_end)
        order_status = weighted_choice(ORDER_STATUS_WEIGHTS)

        city, state, country, _ = random_ph_location()
        shipping_method = random.choices(SHIPPING_METHODS, weights=[0.65, 0.25, 0.10], k=1)[0]

        rows.append({
            "order_id": order_id,
            "customer_id": customer_id,
            "order_date": order_date,
            "order_status": order_status,
            "shipping_address_city": city,
            "shipping_address_state": state,
            "shipping_address_country": country,
            "shipping_method": shipping_method,
            "order_total": 0.0,
            "discount_amount": 0.0,
            "tax_amount": 0.0,
            "shipping_fee": 0.0,
            "batch_date": batch_date
        })

    return pd.DataFrame(rows)


def generate_order_items(orders_df, products_df, start_order_item_id):
    rows = []
    order_item_id = start_order_item_id

    products_lookup = products_df.set_index("product_id").to_dict("index")
    product_ids = products_df["product_id"].tolist()

    order_financials = {}

    for _, order in orders_df.iterrows():
        order_id = int(order["order_id"])
        batch_date = order["batch_date"]
        n_items = random.randint(MIN_ITEMS_PER_ORDER, MAX_ITEMS_PER_ORDER)

        chosen_products = random.sample(product_ids, k=min(n_items, len(product_ids)))

        order_discount_total = 0.0
        subtotal = 0.0

        for product_id in chosen_products:
            product = products_lookup[product_id]
            quantity = random.randint(1, 3)
            unit_price = float(product["price"])

            if random.random() < 0.30:
                discount_amount = safe_round(unit_price * quantity * np.random.uniform(0.05, 0.20), 2)
            else:
                discount_amount = 0.0

            line_total = safe_round(unit_price * quantity - discount_amount, 2)

            rows.append({
                "order_item_id": order_item_id,
                "order_id": order_id,
                "product_id": product_id,
                "seller_id": int(product["seller_id"]),
                "quantity": quantity,
                "unit_price": unit_price,
                "discount_amount": discount_amount,
                "line_total": line_total,
                "batch_date": batch_date
            })

            subtotal += line_total
            order_discount_total += discount_amount
            order_item_id += 1

        shipping_method = order["shipping_method"]
        if shipping_method == "Standard":
            shipping_fee = safe_round(np.random.uniform(50, 120), 2)
        elif shipping_method == "Express":
            shipping_fee = safe_round(np.random.uniform(120, 250), 2)
        else:
            shipping_fee = safe_round(np.random.uniform(180, 350), 2)

        tax_amount = safe_round(subtotal * 0.12, 2)
        order_total = safe_round(subtotal + tax_amount + shipping_fee, 2)

        order_financials[order_id] = {
            "discount_amount": safe_round(order_discount_total, 2),
            "tax_amount": tax_amount,
            "shipping_fee": shipping_fee,
            "order_total": order_total
        }

    return pd.DataFrame(rows), order_financials, order_item_id - 1


def apply_order_financials(orders_df, order_financials):
    orders_df = orders_df.copy()
    for idx, row in orders_df.iterrows():
        order_id = int(row["order_id"])
        fin = order_financials[order_id]
        orders_df.at[idx, "discount_amount"] = fin["discount_amount"]
        orders_df.at[idx, "tax_amount"] = fin["tax_amount"]
        orders_df.at[idx, "shipping_fee"] = fin["shipping_fee"]
        orders_df.at[idx, "order_total"] = fin["order_total"]
    return orders_df


def generate_payments(orders_df, start_payment_id):
    rows = []
    payment_id = start_payment_id

    for _, order in orders_df.iterrows():
        order_id = int(order["order_id"])
        order_status = order["order_status"]
        order_total = float(order["order_total"])
        order_date = pd.to_datetime(order["order_date"])
        batch_date = order["batch_date"]

        payment_method = random.choices(
            PAYMENT_METHODS,
            weights=[0.30, 0.10, 0.25, 0.10, 0.20, 0.05],
            k=1
        )[0]

        if order_status == "cancelled":
            payment_status = random.choices(["failed", "refunded", "pending"], weights=[0.50, 0.30, 0.20], k=1)[0]
        elif order_status == "returned":
            payment_status = random.choices(["paid", "refunded"], weights=[0.40, 0.60], k=1)[0]
        else:
            payment_status = random.choices(["paid", "pending", "failed"], weights=[0.92, 0.05, 0.03], k=1)[0]

        payment_date = order_date + timedelta(hours=random.randint(0, 48))

        if payment_status == "failed":
            amount = 0.0
        else:
            amount = order_total

        rows.append({
            "payment_id": payment_id,
            "order_id": order_id,
            "payment_date": payment_date,
            "payment_method": payment_method,
            "payment_status": payment_status,
            "amount": safe_round(amount, 2),
            "batch_date": batch_date
        })
        payment_id += 1

    return pd.DataFrame(rows), payment_id - 1


def generate_shipping_events(orders_df, start_event_id):
    rows = []
    event_id = start_event_id

    for _, order in orders_df.iterrows():
        order_id = int(order["order_id"])
        order_date = pd.to_datetime(order["order_date"])
        order_status = order["order_status"]
        batch_date = order["batch_date"]
        carrier = random.choice(CARRIERS)
        tracking_number = f"TRK{order_id:08d}"

        events = []

        t1 = order_date + timedelta(minutes=random.randint(5, 180))
        events.append(("order_confirmed", t1))

        if order_status in ["shipped", "delivered", "returned"]:
            t2 = t1 + timedelta(hours=random.randint(4, 24))
            t3 = t2 + timedelta(hours=random.randint(6, 48))
            events.append(("packed", t2))
            events.append(("shipped", t3))

        if order_status in ["delivered", "returned"]:
            t4 = t3 + timedelta(days=random.randint(1, 5))
            t5 = t4 + timedelta(hours=random.randint(2, 12))
            events.append(("out_for_delivery", t4))
            events.append(("delivered", t5))

        if order_status == "returned":
            t6 = t5 + timedelta(days=random.randint(1, 14))
            events.append(("return_requested", t6))

        if order_status == "cancelled":
            t_cancel = t1 + timedelta(hours=random.randint(1, 12))
            events.append(("cancelled", t_cancel))

        for event_type, event_ts in events:
            hub_city, _, _, _ = random_ph_location()
            rows.append({
                "event_id": event_id,
                "order_id": order_id,
                "event_timestamp": event_ts,
                "event_type": event_type,
                "hub_city": hub_city,
                "carrier": carrier,
                "tracking_number": tracking_number,
                "batch_date": batch_date
            })
            event_id += 1

    return pd.DataFrame(rows), event_id - 1


def generate_returns_refunds(orders_df, order_items_df, start_return_id):
    rows = []
    return_id = start_return_id

    eligible_orders = orders_df[orders_df["order_status"].isin(["delivered", "returned"])].copy()

    if eligible_orders.empty:
        return pd.DataFrame(rows), start_return_id - 1

    order_items_grouped = order_items_df.groupby("order_id")

    for _, order in eligible_orders.iterrows():
        order_id = int(order["order_id"])
        order_date = pd.to_datetime(order["order_date"])
        batch_date = order["batch_date"]

        if order["order_status"] == "returned":
            will_return = True
        else:
            will_return = random.random() < RETURN_RATE

        if not will_return:
            continue

        items = order_items_grouped.get_group(order_id).copy()

        n_return_items = random.randint(1, min(2, len(items)))
        return_items = items.sample(n=n_return_items, replace=False)

        for _, item in return_items.iterrows():
            order_item_id = int(item["order_item_id"])
            refund_amount = float(item["line_total"])

            return_date = order_date + timedelta(days=random.randint(3, 20))
            refund_date = return_date + timedelta(days=random.randint(1, 7))

            rows.append({
                "return_id": return_id,
                "order_id": order_id,
                "order_item_id": order_item_id,
                "return_date": return_date,
                "return_reason": random.choice(RETURN_REASONS),
                "refund_amount": safe_round(refund_amount, 2),
                "refund_status": random.choices(["approved", "rejected", "processed"], weights=[0.55, 0.05, 0.40], k=1)[0],
                "refund_date": refund_date,
                "batch_date": batch_date
            })
            return_id += 1

    return pd.DataFrame(rows), return_id - 1


# ============================================================
# VALIDATION
# ============================================================

def validate_data(customers_df, sellers_df, categories_df, products_df,
                  orders_df, order_items_df, payments_df, shipping_df, returns_df):
    print("\n================ VALIDATION CHECKS ================\n")

    assert orders_df["customer_id"].isin(customers_df["customer_id"]).all(), "orders.customer_id FK failed"
    assert products_df["category_id"].isin(categories_df["category_id"]).all(), "products.category_id FK failed"
    assert products_df["seller_id"].isin(sellers_df["seller_id"]).all(), "products.seller_id FK failed"
    assert order_items_df["order_id"].isin(orders_df["order_id"]).all(), "order_items.order_id FK failed"
    assert order_items_df["product_id"].isin(products_df["product_id"]).all(), "order_items.product_id FK failed"
    assert order_items_df["seller_id"].isin(sellers_df["seller_id"]).all(), "order_items.seller_id FK failed"
    assert payments_df["order_id"].isin(orders_df["order_id"]).all(), "payments.order_id FK failed"
    assert shipping_df["order_id"].isin(orders_df["order_id"]).all(), "shipping.order_id FK failed"

    if not returns_df.empty:
        assert returns_df["order_id"].isin(orders_df["order_id"]).all(), "returns.order_id FK failed"
        assert returns_df["order_item_id"].isin(order_items_df["order_item_id"]).all(), "returns.order_item_id FK failed"

    print("FK checks passed.")

    grouped_items = order_items_df.groupby("order_id")["line_total"].sum().reset_index(name="subtotal")
    merged = orders_df.merge(grouped_items, on="order_id", how="left")
    merged["expected_total"] = merged["subtotal"] + merged["tax_amount"] + merged["shipping_fee"]
    merged["diff"] = (merged["order_total"] - merged["expected_total"]).abs()
    max_diff = merged["diff"].max()
    print(f"Max order total difference: {max_diff:.2f}")

    print("\nRow counts:")
    print(f"customers         : {len(customers_df):,}")
    print(f"sellers           : {len(sellers_df):,}")
    print(f"product_category  : {len(categories_df):,}")
    print(f"products          : {len(products_df):,}")
    print(f"orders            : {len(orders_df):,}")
    print(f"order_items       : {len(order_items_df):,}")
    print(f"payments          : {len(payments_df):,}")
    print(f"shipping_events   : {len(shipping_df):,}")
    print(f"returns_refunds   : {len(returns_df):,}")

    print("\nSample order status distribution:")
    print(orders_df["order_status"].value_counts(normalize=True).round(3))
    print("\nValidation completed successfully.\n")


# ============================================================
# FULL LOAD
# ============================================================

def generate_full_load():
    print("Starting FULL LOAD...")

    state = default_state()

    categories_df = generate_product_categories()
    customers_df = generate_customers(FULL_N_CUSTOMERS, 1, batch_date="full_load")
    sellers_df = generate_sellers(FULL_N_SELLERS, 1, batch_date="full_load")
    products_df = generate_products(FULL_N_PRODUCTS, 1, categories_df, sellers_df, batch_date="full_load")
    orders_df = generate_orders(FULL_N_ORDERS, 1, customers_df, batch_date="full_load")

    order_items_df, order_financials, last_order_item_id = generate_order_items(
        orders_df, products_df, start_order_item_id=1
    )
    orders_df = apply_order_financials(orders_df, order_financials)

    payments_df, last_payment_id = generate_payments(orders_df, start_payment_id=1)
    shipping_df, last_event_id = generate_shipping_events(orders_df, start_event_id=1)
    returns_df, last_return_id = generate_returns_refunds(orders_df, order_items_df, start_return_id=1)

    validate_data(
        customers_df, sellers_df, categories_df, products_df,
        orders_df, order_items_df, payments_df, shipping_df, returns_df
    )

    # ---------------- save full load ----------------
    save_csv(customers_df, os.path.join(FULL_LOAD_DIR, "customers.csv"))
    save_csv(sellers_df, os.path.join(FULL_LOAD_DIR, "sellers.csv"))
    save_csv(categories_df, os.path.join(FULL_LOAD_DIR, "product_category.csv"))
    save_csv(products_df, os.path.join(FULL_LOAD_DIR, "products.csv"))
    save_csv(orders_df, os.path.join(FULL_LOAD_DIR, "orders.csv"))
    save_csv(order_items_df, os.path.join(FULL_LOAD_DIR, "order_items.csv"))
    save_csv(payments_df, os.path.join(FULL_LOAD_DIR, "payments.csv"))
    save_csv(shipping_df, os.path.join(FULL_LOAD_DIR, "shipping_events.csv"))
    save_csv(returns_df, os.path.join(FULL_LOAD_DIR, "returns_refunds.csv"))

    # ---------------- initialize master tables ----------------
    write_master(customers_df, "customers.csv")
    write_master(sellers_df, "sellers.csv")
    write_master(categories_df, "product_category.csv")
    write_master(products_df, "products.csv")
    write_master(orders_df, "orders.csv")
    write_master(order_items_df, "order_items.csv")
    write_master(payments_df, "payments.csv")
    write_master(shipping_df, "shipping_events.csv")
    write_master(returns_df, "returns_refunds.csv")

    # ---------------- update state ----------------
    state["last_customer_id"] = int(customers_df["customer_id"].max())
    state["last_seller_id"] = int(sellers_df["seller_id"].max())
    state["last_product_id"] = int(products_df["product_id"].max())
    state["last_order_id"] = int(orders_df["order_id"].max())
    state["last_order_item_id"] = int(last_order_item_id)
    state["last_payment_id"] = int(last_payment_id)
    state["last_event_id"] = int(last_event_id)
    state["last_return_id"] = int(last_return_id) if not returns_df.empty else 0

    save_state(state)

    print("FULL LOAD completed successfully.")


# ============================================================
# INCREMENTAL BATCH
# ============================================================

def generate_incremental_batch(batch_date):
    print(f"Starting INCREMENTAL batch for {batch_date}...")

    state = load_state()

    # require full load / master data first
    categories_df = read_master("product_category.csv")
    customers_master = read_master("customers.csv")
    sellers_master = read_master("sellers.csv")
    products_master = read_master("products.csv")

    n_customers = random.randint(*DAILY_NEW_CUSTOMERS)
    n_sellers = random.randint(*DAILY_NEW_SELLERS)
    n_products = random.randint(*DAILY_NEW_PRODUCTS)
    n_orders = random.randint(*DAILY_NEW_ORDERS)

    print(
        f"Batch sizes -> customers: {n_customers}, sellers: {n_sellers}, "
        f"products: {n_products}, orders: {n_orders}"
    )

    # ---------- new dimension rows ----------
    new_customers = generate_customers(
        n_customers=n_customers,
        start_customer_id=state["last_customer_id"] + 1,
        batch_date=batch_date
    )

    new_sellers = generate_sellers(
        n_sellers=n_sellers,
        start_seller_id=state["last_seller_id"] + 1,
        batch_date=batch_date
    )

    # combine for product generation / order references
    all_customers = pd.concat([customers_master, new_customers], ignore_index=True)
    all_sellers = pd.concat([sellers_master, new_sellers], ignore_index=True)

    new_products = generate_products(
        n_products=n_products,
        start_product_id=state["last_product_id"] + 1,
        categories_df=categories_df,
        sellers_df=all_sellers,
        batch_date=batch_date
    )

    all_products = pd.concat([products_master, new_products], ignore_index=True)

    # ---------- new transactional rows ----------
    new_orders = generate_orders(
        n_orders=n_orders,
        start_order_id=state["last_order_id"] + 1,
        customers_df=all_customers,
        batch_date=batch_date
    )

    new_order_items, order_financials, last_order_item_id = generate_order_items(
        new_orders,
        all_products,
        start_order_item_id=state["last_order_item_id"] + 1
    )
    new_orders = apply_order_financials(new_orders, order_financials)

    new_payments, last_payment_id = generate_payments(
        new_orders,
        start_payment_id=state["last_payment_id"] + 1
    )

    new_shipping, last_event_id = generate_shipping_events(
        new_orders,
        start_event_id=state["last_event_id"] + 1
    )

    new_returns, last_return_id = generate_returns_refunds(
        new_orders,
        new_order_items,
        start_return_id=state["last_return_id"] + 1
    )

    # ---------- validate current batch ----------
    validate_data(
        all_customers,
        all_sellers,
        categories_df,
        all_products,
        new_orders,
        new_order_items,
        new_payments,
        new_shipping,
        new_returns
    )

    # ---------- save incremental batch ----------
    batch_dir = os.path.join(INCREMENTAL_DIR, f"batch_date={batch_date}")
    os.makedirs(batch_dir, exist_ok=True)

    save_csv(new_customers, os.path.join(batch_dir, "customers.csv"))
    save_csv(new_sellers, os.path.join(batch_dir, "sellers.csv"))
    save_csv(new_products, os.path.join(batch_dir, "products.csv"))
    save_csv(new_orders, os.path.join(batch_dir, "orders.csv"))
    save_csv(new_order_items, os.path.join(batch_dir, "order_items.csv"))
    save_csv(new_payments, os.path.join(batch_dir, "payments.csv"))
    save_csv(new_shipping, os.path.join(batch_dir, "shipping_events.csv"))
    save_csv(new_returns, os.path.join(batch_dir, "returns_refunds.csv"))

    # ---------- append to master ----------
    if not new_customers.empty:
        append_master(new_customers, "customers.csv")
    if not new_sellers.empty:
        append_master(new_sellers, "sellers.csv")
    if not new_products.empty:
        append_master(new_products, "products.csv")
    if not new_orders.empty:
        append_master(new_orders, "orders.csv")
    if not new_order_items.empty:
        append_master(new_order_items, "order_items.csv")
    if not new_payments.empty:
        append_master(new_payments, "payments.csv")
    if not new_shipping.empty:
        append_master(new_shipping, "shipping_events.csv")
    if not new_returns.empty:
        append_master(new_returns, "returns_refunds.csv")

    # ---------- update state ----------
    if not new_customers.empty:
        state["last_customer_id"] = int(new_customers["customer_id"].max())
    if not new_sellers.empty:
        state["last_seller_id"] = int(new_sellers["seller_id"].max())
    if not new_products.empty:
        state["last_product_id"] = int(new_products["product_id"].max())
    if not new_orders.empty:
        state["last_order_id"] = int(new_orders["order_id"].max())
    if not new_order_items.empty:
        state["last_order_item_id"] = int(last_order_item_id)
    if not new_payments.empty:
        state["last_payment_id"] = int(last_payment_id)
    if not new_shipping.empty:
        state["last_event_id"] = int(last_event_id)
    if not new_returns.empty:
        state["last_return_id"] = int(last_return_id)

    save_state(state)

    print(f"INCREMENTAL batch for {batch_date} completed successfully.")


# ============================================================
# CLI
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(description="Incremental E-commerce Mock Data Generator")
    parser.add_argument(
        "--mode",
        required=True,
        choices=["full", "incremental"],
        help="full = historical full load, incremental = generate one daily batch"
    )
    parser.add_argument(
        "--batch-date",
        required=False,
        help="Batch date in YYYY-MM-DD format. Required for incremental mode."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.mode == "full":
        generate_full_load()

    elif args.mode == "incremental":
        if not args.batch_date:
            raise ValueError("For incremental mode, you must provide --batch-date YYYY-MM-DD")

        # validate date format
        try:
            pd.to_datetime(args.batch_date, format="%Y-%m-%d")
        except Exception:
            raise ValueError("batch-date must be in YYYY-MM-DD format")

        generate_incremental_batch(args.batch_date)


if __name__ == "__main__":
    main()