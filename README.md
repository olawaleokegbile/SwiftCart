# 🛒 SwiftCart

SwiftCart is a modern eCommerce web application built with **Django**, **TailwindCSS**, and **JavaScript**, designed for smooth online shopping experiences. It supports cart management, checkout with multiple payment methods (Pay on Delivery, Bank Transfer, Paystack), user authentication via **Django Allauth**, and a responsive dashboard interface.

---

## 🚀 Features

- **Authentication & Authorization**
  - User registration and login/logout using **Django Allauth**
  - Session management for both authenticated and anonymous users

- **Product Management**
  - Store page displaying all products
  - Product detail page with "Add to Cart" option

- **Cart System**
  - Add/Remove products from cart
  - Cart count updates dynamically (AJAX-powered)
  - Session-based cart handling for anonymous users

- **Checkout & Payments**
  - Multiple payment methods:
    - ✅ Pay on Delivery
    - ✅ Bank Transfer
    - ✅ Paystack Integration
  - Secure order completion flow (payment verification before order finalization)

- **Dashboard & UI**
  - Sidebar navigation
  - Dark/Light mode toggle
  - Responsive layout with TailwindCSS
  - Dynamic cart badge with item count

---

## 🛠️ Tech Stack

- **Backend**: Django, Django Allauth
- **Frontend**: TailwindCSS, Vanilla JavaScript
- **Payments**: Paystack API Integration
- **Database**: SQLite (default, can be swapped for PostgreSQL/MySQL)

---

## 📂 Project Structure

```
SwiftCart/
│   manage.py
│   requirements.txt
│   README.md
│
├───swiftcart/              # Core Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├───store/                  # Store app (products, cart, checkout)
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   └── static/
│
├───templates/              # Shared templates (base.html, etc.)
│
└───static/                 # Global static files (CSS, JS, images)
```

---

## ⚙️ Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/yourusername/SwiftCart.git
cd SwiftCart
```

### 2️⃣ Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Run migrations
```bash
python manage.py migrate
```

### 5️⃣ Create a superuser
```bash
python manage.py createsuperuser
```

### 6️⃣ Run the development server
```bash
python manage.py runserver
```
Now visit: 👉 http://127.0.0.1:8000

---

## 🔑 Paystack Setup

1. Create an account on [Paystack](https://paystack.com).
2. Get your **Public Key** and **Secret Key** from the dashboard.
3. Add them to your environment or `settings.py`:

```python
PAYSTACK_PUBLIC_KEY = "pk_test_xxxxxxxxx"
PAYSTACK_SECRET_KEY = "sk_test_xxxxxxxxx"
```

If using `.env`:
```
PAYSTACK_PUBLIC_KEY=pk_test_xxxxxxxxx
PAYSTACK_SECRET_KEY=sk_test_xxxxxxxxx
```

---

## 🌗 Theme Toggle
- The app has a **light/dark mode** toggle button.
- Implemented with TailwindCSS and JavaScript.

---

## 📸 Screenshots
*(Add screenshots of Store page, Cart, and Checkout once deployed)*

---

## 📌 Roadmap
- [ ] Add product categories & filters
- [ ] Order history for users
- [ ] Admin dashboard for managing products
- [ ] Email notifications on order confirmation

---

## 🤝 Contributing
Pull requests are welcome! To contribute:
1. Fork the repo
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit changes (`git commit -m "Added new feature"`)
4. Push to branch (`git push origin feature-branch`)
5. Create a Pull Request

---

## 📜 License
This project is licensed under the MIT License.

---

## 👨‍💻 Author
- **Olawale Okegbile**  

