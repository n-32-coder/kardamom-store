# KARDAMOM — Premium Cardamom Store

E-commerce web app for selling cardamom online. Django + SQLite (dev) / MySQL-ready, premium dark GUI.

## Features
- Browse, search, filter (category / price / pack size), product detail with gallery + specs
- Cart, checkout, orders with status lifecycle (pending → confirmed → processing → shipped → delivered / cancelled)
- Order confirmation email (console backend in dev)
- Wishlist, product reviews with verified-purchase badge
- Auth: register / login / logout / profile (custom `Customer` user model)
- Staff dashboard: revenue, orders by status, top products, low-stock alerts
- Admin: products, categories, images, reviews, wishlist, carts, orders + items
- Payment methods: COD / UPI working; Razorpay + Stripe wired live — order created in Razorpay/Stripe when real keys are set, HMAC signature verified on callback, graceful error when keys are placeholders

## Run
```bash
cd /path/to/project
python3 -m venv .venv && source .venv/bin/activate
pip install django
python manage.py migrate
python seed_kardamom.py     # demo data + admin user (password printed by set_admin_pw.py)
python manage.py runserver  # http://localhost:8000, admin at /admin
```

To go live with online payments, set env keys: `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`,
`STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`.

## Layout
- `config/` — settings, root URLs (`/healthz/` probe included)
- `customers/` — custom user, register/profile
- `products/` — catalogue, reviews, wishlist
- `cart/` — shopping cart
- `orders/` — checkout, orders, staff dashboard, gateway helpers
- `kardamom/templates/`, `kardamom/static/` — premium GUI + product artwork
- `k8s/` — namespace, Secret, PVC, Deployment (3 replicas, probes, rolling updates),
  Service (load balancing), Ingress TLS, HPA (2–5, CPU/memory), RBAC, NetworkPolicy
- `monitoring/` — ServiceMonitor, PrometheusRule alerts, Grafana dashboard
- `serverless/order-notify/` — Knative event-driven notification function
- `.github/workflows/ci-cd.yaml` — build → test → GHCR image push
- `seed_kardamom.py`, `verify_*.py` — seed + checks

## Deploy (K8s)
```bash
kubectl apply -f k8s/
kubectl apply -f monitoring/
kubectl apply -f serverless/order-notify/service.yaml
# Images: ghcr.io/<owner>/kardamom:latest (CI pushes on main)
```

## SRS
Original spec: `Downloads/KARDAMOM.pdf`. Plan: `KARDAMOM_Project_Plan.md`.
