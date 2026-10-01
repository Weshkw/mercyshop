# Mercy Beauty Shop

An online shop and back-office for a small beauty retailer, built with Django.
Customers browse makeup, skincare and hair-care products and fill a cart;
staff manage the catalogue and record the shop's day-to-day running costs.

## Features

**For customers**

- Product catalogue with photos, prices and a photo gallery per product.
- Search across product names and descriptions.
- A cart per visitor, kept in their session: add, remove and change quantities
  without reloading the page, with a running total and a cart badge in the header.
- Featured product videos on the home page.

**For staff**

- Sign in with a national ID number.
- Add products (with several gallery photos at once) and featured videos;
  only accounts with the matching permission can do this.
- Record petty costs per activity – transport, lunch, airtime and any other
  cost – and see running totals of their own spending.
- Full management of products, orders, costs and staff in the Django admin.

## Project layout

| Path | What it holds |
| --- | --- |
| `generalshop/models.py` | Staff accounts, products, gallery images, videos, orders and petty costs |
| `generalshop/cart.py` | The session cart and its add / subtract / remove actions |
| `generalshop/views.py` | Catalogue, cart, product and video upload, and expense pages |
| `generalshop/forms.py` | Product (with multi-image gallery), video and petty-cost forms |
| `static/scripts/cart.js` | Updates the cart in place from any cart button |
| `smallenterprisemanagement/settings.py` | Settings, all read from environment variables |

## Getting started

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py createsuperuser   # asks for an ID number, names and phone number
python manage.py runserver
```

Open http://localhost:8000/ for the shop and http://localhost:8000/admin/ for
the back-office. To let a staff member add products, give them the
*Can add product* permission in the admin.

## Configuration

Settings are read from environment variables. With none set, the app runs in
local development mode on SQLite. See [`.env.example`](.env.example) for the
full list. The app refuses to start with debug off and no secret key.

## Development

```bash
ruff check .               # lint
ruff format .              # format
python manage.py test      # run the test suite
```

The same checks run on every push through GitHub Actions.
