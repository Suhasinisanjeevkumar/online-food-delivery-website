from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
import sqlite3

restaurants_bp = Blueprint('restaurants', __name__)

def get_db_connection():
    conn = sqlite3.connect('food_delivery.db')
    conn.row_factory = sqlite3.Row
    return conn

@restaurants_bp.route('/restaurant/<int:restaurant_id>')
@login_required
def restaurant_menu(restaurant_id):
    conn = get_db_connection()
    restaurant = conn.execute('SELECT * FROM restaurants WHERE id = ?', (restaurant_id,)).fetchone()
    menu_items = conn.execute('SELECT * FROM menu_items WHERE restaurant_id = ?', (restaurant_id,)).fetchall()
    conn.close()
    return render_template('restaurant_menu.html', restaurant=restaurant, menu_items=menu_items)

@restaurants_bp.route('/api/restaurants/search')
@login_required
def search_restaurants():
    query = request.args.get('q', '')
    category_id = request.args.get('category_id')
    
    conn = get_db_connection()
    
    if query:
        restaurants = conn.execute('''
            SELECT DISTINCT r.* FROM restaurants r 
            JOIN menu_items m ON r.id = m.restaurant_id 
            WHERE (m.name LIKE ? OR m.description LIKE ? OR r.name LIKE ?)
            AND (? IS NULL OR r.category_id = ?)
        ''', (f'%{query}%', f'%{query}%', f'%{query}%', category_id, category_id)).fetchall()
    else:
        restaurants = conn.execute('SELECT * FROM restaurants WHERE category_id = ?', (category_id,)).fetchall()
    
    conn.close()
    
    restaurants_list = []
    for restaurant in restaurants:
        restaurants_list.append(dict(restaurant))
    
    return jsonify(restaurants_list)