# 🛒 VipraTech Store — Django + Stripe Payment Integration

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Django](https://img.shields.io/badge/Django-4.x-green?style=flat-square&logo=django)
![Stripe](https://img.shields.io/badge/Stripe-Payment_Gateway-635BFF?style=flat-square&logo=stripe)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple?style=flat-square&logo=bootstrap)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=flat-square)

> A single-page Django e-commerce store with real Stripe Checkout integration, webhook-based order confirmation, and 4-layer double-payment prevention — built to understand production-grade payment flows that most tutorials skip.

---

## 📌 What This Project Does

Users can browse products, select quantities, and complete purchases via **Stripe Checkout**. Orders are confirmed server-side via webhooks — not browser redirects — making the flow reliable even if the user closes the tab after paying.

Built this specifically to understand **real payment gateway integration** at a deeper level than surface-level tutorials.

---

## ✨ Features

- 🛍️ Product listing with quantity selector
- 💰 Live total calculation (Vanilla JavaScript)
- 💳 Stripe Checkout integration (test mode)
- 🔔 Webhook handler for reliable server-side order confirmation
- 🔒 Session-based order tracking (no login required)
- ⚡ 4-layer double-payment prevention

---

## 🧠 My Approach & Decisions

### Why Stripe Checkout instead of Payment Intents?
Stripe Checkout handles payment UI, PCI compliance, and card validation out of the box. Payment Intents would have required building and hosting a custom card form — more complexity with no benefit at this scope.

### How I Prevented Double Charges — 4 Layers

| Layer | Method | Why |
|-------|--------|-----|
| Frontend | Buy button disables on click | Prevents accidental double-click |
| Stripe | UUID idempotency key per order | Retried requests don't create duplicate charges |
| Database | `select_for_update()` | Prevents race conditions on concurrent requests |
| Status check | Only `pending` → `paid` transition allowed | Dead orders can never be re-charged |

### Why a Webhook Instead of Success URL?
The success URL is unreliable — if the user closes the browser after paying but before redirect, the order stays `pending` forever. The webhook fires **server-side regardless of browser state**, so every payment is confirmed.

### Session-Based Tracking
No login system needed. Django's built-in session framework assigns each browser a unique session key — orders are tied to it cleanly.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django, Python |
| Payments | Stripe Checkout API + Webhooks |
| Database | SQLite (development) |
| Frontend | HTML, Bootstrap 5, Vanilla JS |
| Concurrency | `select_for_update()`, `transaction.atomic()` |

---

## 📂 Project Structure

```
viprashop/
├── store/
│   ├── models.py          # Product, Order, OrderItem
│   ├── views.py           # Checkout flow + webhook handler
│   ├── urls.py
│   └── templates/
│       └── store/
│           └── index.html
├── manage.py
├── requirements.txt
└── .env.example
```

---

## 🚀 Setup & Run

### 1. Clone the repo
```bash
git clone https://github.com/AshishChaubey2003/viprashop.git
cd viprashop
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment variables
```bash
cp .env.example .env
```

```env
SECRET_KEY=your-django-secret-key
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
BASE_URL=http://localhost:8000
DEBUG=True
```

### 4. Run migrations & start server
```bash
python manage.py migrate
python manage.py runserver
```

### 5. Start Stripe webhook listener (local testing)
```bash
stripe listen --forward-to localhost:8000/webhook/
```

Open `http://localhost:8000`

---

## 💳 Test Payments

| Field | Value |
|-------|-------|
| Card number | `4242 4242 4242 4242` |
| Expiry | Any future date |
| CVV | Any 3 digits |

---

## 🚀 Roadmap

- [ ] Stock management & inventory tracking
- [ ] Admin dashboard for order management
- [ ] User login & order history
- [ ] PostgreSQL for production deployment
- [ ] Deploy on Render with live Stripe webhook

---

## 📄 License

MIT License — open source and free to use.

---

<p align="center">Built by <a href="https://github.com/AshishChaubey2003">Ashish Kumar Chaubey</a> — B.Tech CSE 2025 | Lucknow, India</p>
<p align="center">
  <a href="https://www.linkedin.com/in/ashishchaubey2dec/">LinkedIn</a> •
  <a href="https://personal-portfolio-website-one-azure.vercel.app/">Portfolio</a> •
  <a href="mailto:sashishchaubey1234@gmail.com">Email</a>
</p>
