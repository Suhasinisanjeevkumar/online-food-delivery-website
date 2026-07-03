from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database configuration
DATABASE = 'food_delivery.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            phone TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Payment details table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payment_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            card_type TEXT,
            last_four_digits TEXT,
            expiry_date TEXT,
            cardholder_name TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders (id)
        )
    ''')
    
    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image_url TEXT
        )
    ''')
    
    # Restaurants table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            description TEXT,
            address TEXT,
            phone TEXT,
            rating REAL DEFAULT 0.0,
            image_url TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    # Menu items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            image_url TEXT,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
        )
    ''')
    
    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            address TEXT,
            payment_method TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Order items table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            menu_item_id INTEGER,
            quantity INTEGER,
            price REAL,
            FOREIGN KEY (order_id) REFERENCES orders (id),
            FOREIGN KEY (menu_item_id) REFERENCES menu_items (id)
        )
    ''')
    
    # User addresses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            address TEXT NOT NULL,
            is_default BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Insert sample data
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        sample_categories = [
            ('Meals', '/static/images/meals.jpg'),
            ('Fast Food', '/static/images/fastfood.jpg'),
            ('Drinks', '/static/images/drinks.jpg'),
            ('Desserts', '/static/images/desserts.jpg')
        ]
        cursor.executemany("INSERT INTO categories (name, image_url) VALUES (?, ?)", sample_categories)
        
        sample_restaurants = [
            ('North Indian Dhaba', 1, 'Authentic North Indian meals', '123 Main St', '555-0101', 4.5, '/static/images/dhaba.jpg'),
            ('Pizza Palace', 2, 'Best pizza in town', '456 Oak St', '555-0102', 4.3, '/static/images/pizza.jpg'),
            ('Cool Drinks', 3, 'Refreshing beverages', '789 Pine St', '555-0103', 4.2, '/static/images/drinkshop.jpg'),
            ('Sweet Treats', 4, 'Delicious desserts', '321 Elm St', '555-0104', 4.6, '/static/images/dessert.jpg')
        ]
        cursor.executemany("INSERT INTO restaurants (name, category_id, description, address, phone, rating, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)", sample_restaurants)
        
        sample_menu_items = [
            (1, 'North Indian Thali', 'Complete meal with roti, rice, dal, and vegetables', 12.99, '/static/images/thali.jpg'),
            (1, 'Butter Chicken', 'Creamy butter chicken with naan', 15.99, '/static/images/butterchicken.jpg'),
            (2, 'Margherita Pizza', 'Classic cheese and tomato pizza', 10.99, '/static/images/margherita.jpg'),
            (2, 'Pepperoni Pizza', 'Pepperoni with extra cheese', 12.99, '/static/images/pepperoni.jpg'),
            (3, 'Mango Shake', 'Fresh mango milkshake', 4.99, '/static/images/mangoshake.jpg'),
            (3, 'Cold Coffee', 'Iced coffee with cream', 3.99, '/static/images/coldcoffee.jpg'),
            (4, 'Chocolate Cake', 'Rich chocolate cake slice', 5.99, '/static/images/chocolatecake.jpg'),
            (4, 'Ice Cream Sundae', 'Vanilla ice cream with toppings', 6.99, '/static/images/sundae.jpg')
        ]
        cursor.executemany("INSERT INTO menu_items (restaurant_id, name, description, price, image_url) VALUES (?, ?, ?, ?, ?)", sample_menu_items)
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User:
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return User(user['id'], user['username'], user['email'])
    return None

# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            user_obj = User(user['id'], user['username'], user['email'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        phone = request.form.get('phone', '')
        
        if len(password) < 6 or len(password) > 12:
            flash('Password must be between 6 and 12 characters')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, password, phone) VALUES (?, ?, ?, ?)',
                        (username, email, hashed_password, phone))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db_connection()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()
    return render_template('dashboard.html', categories=categories)

@app.route('/category/<int:category_id>')
@login_required
def category_restaurants(category_id):
    search_query = request.args.get('search', '')
    conn = get_db_connection()
    
    if search_query:
        restaurants = conn.execute('''
            SELECT DISTINCT r.* FROM restaurants r 
            JOIN menu_items m ON r.id = m.restaurant_id 
            WHERE r.category_id = ? AND (m.name LIKE ? OR m.description LIKE ?)
        ''', (category_id, f'%{search_query}%', f'%{search_query}%')).fetchall()
    else:
        restaurants = conn.execute('SELECT * FROM restaurants WHERE category_id = ?', (category_id,)).fetchall()
    
    category = conn.execute('SELECT * FROM categories WHERE id = ?', (category_id,)).fetchone()
    conn.close()
    
    return render_template('restaurants.html', restaurants=restaurants, category=category, search_query=search_query)

@app.route('/restaurant/<int:restaurant_id>')
@login_required
def restaurant_menu(restaurant_id):
    conn = get_db_connection()
    restaurant = conn.execute('SELECT * FROM restaurants WHERE id = ?', (restaurant_id,)).fetchone()
    menu_items = conn.execute('SELECT * FROM menu_items WHERE restaurant_id = ?', (restaurant_id,)).fetchall()
    conn.close()
    return render_template('restaurant_menu.html', restaurant=restaurant, menu_items=menu_items)

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    item_id = request.form['item_id']
    quantity = int(request.form['quantity'])
    
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM menu_items WHERE id = ?', (item_id,)).fetchone()
    conn.close()
    
    if 'cart' not in session:
        session['cart'] = {}
    
    cart = session['cart']
    if item_id in cart:
        cart[item_id]['quantity'] += quantity
    else:
        cart[item_id] = {
            'name': item['name'],
            'price': float(item['price']),
            'quantity': quantity,
            'restaurant_id': item['restaurant_id']
        }
    
    session['cart'] = cart
    session.modified = True
    
    return jsonify({'success': True, 'cart_count': len(cart)})

@app.route('/cart')
@login_required
def cart():
    cart_items = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart_items.values())
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart', methods=['POST'])
@login_required
def update_cart():
    item_id = request.form['item_id']
    quantity = int(request.form['quantity'])
    
    cart = session.get('cart', {})
    if quantity <= 0:
        cart.pop(item_id, None)
    else:
        cart[item_id]['quantity'] = quantity
    
    session['cart'] = cart
    session.modified = True
    
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        address = request.form['address']
        payment_method = request.form['payment_method']
        
        cart = session.get('cart', {})
        if not cart:
            flash('Your cart is empty', 'error')
            return redirect(url_for('cart'))
        
        total = sum(item['price'] * item['quantity'] for item in cart.values())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Create order
            cursor.execute('''
                INSERT INTO orders (user_id, total_amount, address, payment_method, status) 
                VALUES (?, ?, ?, ?, ?)
            ''', (current_user.id, total, address, payment_method, 'confirmed'))
            order_id = cursor.lastrowid
            
            # Add order items
            for item_id, item in cart.items():
                cursor.execute('''
                    INSERT INTO order_items (order_id, menu_item_id, quantity, price) 
                    VALUES (?, ?, ?, ?)
                ''', (order_id, item_id, item['quantity'], item['price']))
            
            conn.commit()
            
            # Clear cart after successful order
            session.pop('cart', None)
            flash('Order placed successfully!', 'success')
            return redirect(url_for('profile'))
            
        except Exception as e:
            conn.rollback()
            flash('Error placing order. Please try again.', 'error')
            return redirect(url_for('checkout'))
        finally:
            conn.close()
    
    # GET request - show checkout form
    cart_items = session.get('cart', {})
    if not cart_items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('cart'))
    
    total = sum(item['price'] * item['quantity'] for item in cart_items.values())
    
    # Get user addresses
    conn = get_db_connection()
    addresses = conn.execute('SELECT * FROM user_addresses WHERE user_id = ?', (current_user.id,)).fetchall()
    conn.close()
    
    return render_template('checkout.html', cart_items=cart_items, total=total, addresses=addresses)

@app.route('/save_address', methods=['POST'])
@login_required
def save_address():
    address = request.form['address']
    if address.strip():
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO user_addresses (user_id, address) VALUES (?, ?)', (current_user.id, address))
            conn.commit()
            flash('Address saved successfully!', 'success')
        except sqlite3.Error as e:
            flash('Error saving address', 'error')
        finally:
            conn.close()
    else:
        flash('Address cannot be empty', 'error')
    
    return redirect(url_for('checkout'))

@app.route('/profile')
@login_required
def profile():
    conn = get_db_connection()
    addresses = conn.execute('SELECT * FROM user_addresses WHERE user_id = ?', (current_user.id,)).fetchall()
    orders = conn.execute('''
        SELECT o.*, COUNT(oi.id) as item_count 
        FROM orders o 
        LEFT JOIN order_items oi ON o.id = oi.order_id 
        WHERE o.user_id = ? 
        GROUP BY o.id 
        ORDER BY o.created_at DESC
    ''', (current_user.id,)).fetchall()
    conn.close()
    return render_template('profile.html', addresses=addresses, orders=orders)

@app.route('/update_order_status', methods=['POST'])
@login_required
def update_order_status():
    order_id = request.form['order_id']
    status = request.form['status']
    feedback = request.form.get('feedback', '')
    
    conn = get_db_connection()
    conn.execute('UPDATE orders SET status = ? WHERE id = ? AND user_id = ?', (status, order_id, current_user.id))
    conn.commit()
    conn.close()
    
    flash('Order status updated successfully!', 'success')
    return redirect(url_for('profile'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('cart', None)
    return redirect(url_for('login'))
# @app.route('/checkout', methods=['GET', 'POST'])
# @login_required
# def checkout():
#     if request.method == 'POST':
#         address = request.form['address']
#         payment_method = request.form['payment_method']
        
#         # Get card details if payment method is Card
#         card_details = {}
#         if payment_method == 'Card':
#             card_details = {
#                 'card_type': request.form.get('card_type', ''),
#                 'card_number': request.form.get('card_number', '')[-4:],  # Store only last 4 digits
#                 'expiry_date': request.form.get('expiry_date', ''),
#                 'cardholder_name': request.form.get('cardholder_name', '')
#             }
        
#         cart = session.get('cart', {})
#         if not cart:
#             flash('Your cart is empty', 'error')
#             return redirect(url_for('cart'))
        
#         total = sum(item['price'] * item['quantity'] for item in cart.values())
        
#         conn = get_db_connection()
#         cursor = conn.cursor()
        
#         try:
#             # Create order
#             cursor.execute('''
#                 INSERT INTO orders (user_id, total_amount, address, payment_method, status) 
#                 VALUES (?, ?, ?, ?, ?)
#             ''', (current_user.id, total, address, payment_method, 'confirmed'))
#             order_id = cursor.lastrowid
            
#             # Add order items
#             for item_id, item in cart.items():
#                 cursor.execute('''
#                     INSERT INTO order_items (order_id, menu_item_id, quantity, price) 
#                     VALUES (?, ?, ?, ?)
#                 ''', (order_id, item_id, item['quantity'], item['price']))
            
#             # Store card details if payment is by card
#             if payment_method == 'Card' and card_details:
#                 cursor.execute('''
#                     INSERT INTO payment_details (order_id, card_type, last_four_digits, expiry_date, cardholder_name)
#                     VALUES (?, ?, ?, ?, ?)
#                 ''', (order_id, card_details['card_type'], card_details['card_number'], 
#                       card_details['expiry_date'], card_details['cardholder_name']))
            
#             conn.commit()
            
#             # Clear cart after successful order
#             session.pop('cart', None)
            
#             # Show appropriate success message
#             if payment_method == 'Card':
#                 flash('Order placed successfully! Payment processed.', 'success')
#             else:
#                 flash('Order placed successfully!', 'success')
                
#             return redirect(url_for('profile'))
            
#         except Exception as e:
#             conn.rollback()
#             flash('Error placing order. Please try again.', 'error')
#             return redirect(url_for('checkout'))
#         finally:
#             conn.close()
    
#     # GET request - show checkout form
#     cart_items = session.get('cart', {})
#     if not cart_items:
#         flash('Your cart is empty', 'error')
#         return redirect(url_for('cart'))
    
#     total = sum(item['price'] * item['quantity'] for item in cart_items.values())
    
#     # Get user addresses
#     conn = get_db_connection()
#     addresses = conn.execute('SELECT * FROM user_addresses WHERE user_id = ?', (current_user.id,)).fetchall()
#     conn.close()
    
#     return render_template('checkout.html', cart_items=cart_items, total=total, addresses=addresses)

if __name__ == '__main__':
    app.run(debug=True)