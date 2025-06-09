
# 🚗 Django Pricing Module



## 📦 Features

- ✅ Dynamic day-wise pricing config
- ⏱️ Time multipliers (e.g. per-hour price change)
- 🕰️ Waiting charges (per minute after grace period)
- 📊 Auto-logging on updates with user tracking
- 🔍 Easy API testing with Postman and curl
- ✅ Unit tests included

---

## 🚀 Quick Start Guide

### 1. Clone the Repo

```bash
git clone https://github.com/shubham-bit-hash/pricingModule.git
cd pricingModule
````

### 2. Create & Activate Virtual Environment

```bash
python3 -m venv env
source env/bin/activate        # Windows: env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Create Superuser (Optional for Admin Access)

```bash
python manage.py createsuperuser
```

### 6. Run the Development Server

```bash
python manage.py runserver
```

Visit the app at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## ✅ Run Test Cases

### Django Unit Tests

```bash
python manage.py test pricing
```

### Run Custom Script (`tests.py`)

```bash
python tests.py
```

---

## 🔁 Sample API Usage

### Example: Create a Pricing Configuration (cURL)

```bash
curl -X POST http://127.0.0.1:8000/api/pricing-configs/ \
-H "Content-Type: application/json" \
-d '{
    "distance": 8.5,
    "ride_time": 95,
    "waiting_time": 10,
    "day_of_week": "MON"
  }'
}'
```

## 📌 Dependencies (requirements.txt)

Example of what's inside:

```
Django>=4.2,<5.0
djangorestframework
```

Install them using:

```bash
pip install -r requirements.txt
```

---

## 👤 Author

**Shubham Shingare**
🔗 GitHub: [shubham-bit-hash](https://github.com/shubham-bit-hash)

---

