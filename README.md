# VipraTech Store

A simple e-commerce store built with Django and Stripe payment integration.

## What I Built

A single-page store where users can browse products, select quantities, and complete purchases via Stripe Checkout. Orders appear on the same page after payment.

I built this to get hands-on experience with real payment gateway integration — something most tutorials skip over.

---

## Features

- Product listing with quantity selector
- Live total calculation (JavaScript)
- Stripe Checkout integration (test mode)
- Webhook handler for reliable order confirmation
- Session-based order tracking (no login required)
- Double-payment prevention

---

## My Approach & Decisions

### Why Stripe Checkout instead of Payment Intents?

I went with Stripe Checkout because it handles the payment UI, PCI compliance, and card validation out of the box. Payment Intents would have required me to build and host the card form myself — more complexity with less benefit for this scope.

### How I prevented double charges

This was the most interesting problem to solve. I used four layers:

1. **Frontend** — Buy button disables immediately on click
2. **Idempotency key** — Each order gets a UUID sent to Stripe, so retried requests don't create duplicate charges
3. **Database lock** — `select_for_update()` prevents race conditions if two requests hit simultaneously
4. **Status check** — Only `pending` orders get marked as `paid`

### Why a webhook?

The success URL alone isn't reliable — if the user closes the browser after paying but before the redirect, the order stays `pending` forever. The webhook fires server-side regardless of what the browser does, so orders always get confirmed.

### Session-based tracking

Since there's no login system, I used Django's built-in session framework to identify users by their session key. Each browser gets a unique session, and orders are tied to it.

---

## Tech Stack

- **Backend:** Django, Python
- **Payments:** Stripe Checkout API
- **Database:** SQLite (development)
- **Frontend:** HTML, Bootstrap 5, Vanilla JS
- **Other:** Django sessions, `select_for_update`, `transaction.atomic`

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/AshishChaubey2003/viprashop.git
cd viprashop
```

### 2. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

pip install -r requirements.txt
```

### 3. Create `.env` file

```bash
cp .env.example .env
```

Add your keys to `.env`:

```
SECRET_KEY=your-django-secret-key
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
BASE_URL=http://localhost:8000
DEBUG=True
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Start the server

```bash
python manage.py runserver
```

### 6. Set up Stripe webhook (for local testing)

```bash
stripe listen --forward-to localhost:8000/webhook/
```

Open `http://localhost:8000` in your browser.

---

## Testing Payments

Use Stripe's test card:

| Field | Value |
|-------|-------|
| Card number | `4242 4242 4242 4242` |
| Expiry | Any future date |
| CVV | Any 3 digits |

---

## Project Structure

```
viprashop/
├── store/
│   ├── models.py      # Product, Order, OrderItem
│   ├── views.py       # Checkout flow + webhook handler
│   ├── urls.py
│   └── templates/
│       └── store/
│           └── index.html
├── manage.py
├── requirements.txt
└── .env.example
```

---

## Known Limitations

- No stock management (can oversell)
- Orders shown to all sessions on index (commented-out filter — intentional for demo)
- No admin UI for order management beyond Django admin

These would be the next things I'd add in a production version.
