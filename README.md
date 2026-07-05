# 🍔 Online Food Delivery Website

A full-stack **Flask-based Online Food Delivery System** that allows users to browse restaurants, explore menus, add items to the cart, and place orders online through a simple and user-friendly interface.

---

## 🚀 Features

- 👤 User Registration & Login
- 🍽️ Browse Restaurants and Food Items
- 🛒 Add Items to Cart
- 📦 Place Orders
- 🧾 View Order History
- 🔐 Secure Authentication using Flask-Login
- 🗄️ SQLite Database Integration
- 📱 Responsive User Interface

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML5, CSS3, JavaScript
- **Database:** SQLite
- **Authentication:** Flask-Login
- **Tools:** Git, GitHub

---

# 📁 Project Structure

```plaintext
online-food-delivery-website/
│
├── backend/
│   ├── app.py                     # Main Flask application
│   ├── food_delivery.db           # SQLite database
│   ├── package.json               # Project dependencies (if applicable)
│   │
│   ├── routes/                    # Flask route files
│   │
│   ├── templates/                 # HTML templates
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── register.html
│   │   ├── menu.html
│   │   ├── cart.html
│   │   └── ...
│   │
│   └── static/                    # Static files
│       ├── css/
│       ├── js/
│       └── images/
│
├── frontend/                      # Frontend files (if separate)
│
├── instance/                      # Instance configuration
│
├── config.py                      # Configuration settings
├── requirements.txt               # Python dependencies
├── README.md                      # Project documentation
└── .gitignore                     # Git ignore file
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/Suhasinisanjeevkumar/online-food-delivery-website.git
```

### 2. Navigate to the project directory

```bash
cd online-food-delivery-website/backend
```

### 3. Create a virtual environment (Optional)

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

**Windows**

```bash
.venv\Scripts\activate
```

**Mac/Linux**

```bash
source .venv/bin/activate
```

### 5. Install the required dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Flask application

```bash
python app.py
```

---

## 🌐 Access the Application

Open your browser and visit:

```text
http://127.0.0.1:5000/
```

---

## 👨‍💻 Author

**Suhasini Sanjeev Kumar**

GitHub: https://github.com/Suhasinisanjeevkumar
