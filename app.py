import json
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for

# Initialize the Flask application
app = Flask(__name__, template_folder='.')

# --- Data Loading ---
def load_orders():
    """Loads order data from the JSON file."""
    data_file = Path(__file__).parent / "orders.json"
    try:
        with open(data_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # In a real app, you'd want more robust error handling/logging
        return {}

def save_orders(orders_data):
    """Saves the orders data to the JSON file."""
    data_file = Path(__file__).parent / "orders.json"
    with open(data_file, 'w') as f:
        # Use indent for a readable JSON file
        json.dump(orders_data, f, indent=2)

ORDERS_DATA = load_orders()

# --- Routes ---
@app.route('/')
def index():
    """Renders the main search page."""
    return render_template('index.html')

@app.route('/order/<order_id>')
def find_order_get(order_id):
    """Displays details for a specific order, accessible via GET request."""
    order_details = ORDERS_DATA.get(order_id.upper())
    if order_details:
        # Use a copy to avoid modifying the global data
        details_copy = order_details.copy()
        details_copy['id'] = order_id.upper()
        return render_template('order_details.html', order=details_copy)
    else:
        return render_template('index.html', error=f"Lift Order '{order_id}' not found.")

@app.route('/order', methods=['POST'])
def find_order_post():
    """Handles the order lookup form submission."""
    order_id = request.form.get('order_id')
    
    if not order_id:
        return render_template('index.html', error="Please enter a lift order number.")

    return redirect(url_for('find_order_get', order_id=order_id))

@app.route('/new')
def new_order():
    """Renders the page to create a new order."""
    return render_template('edit_order.html')

@app.route('/edit/<order_id>')
def edit_order(order_id):
    """Renders the edit page for an existing order."""
    order_details = ORDERS_DATA.get(order_id.upper())
    if order_details:
        details_copy = order_details.copy()
        details_copy['id'] = order_id.upper()
        return render_template('edit_order.html', order=details_copy)
    else:
        return render_template('index.html', error=f"Cannot edit. Lift Order '{order_id}' not found.")

@app.route('/save', methods=['POST'])
def save_order():
    """Saves a new or updated order."""
    form_data = request.form
    order_id = form_data['order_id'].upper()

    # Look for the order in our data (case-insensitive for user-friendliness)
    new_order_data = {
        "customer_name": form_data['customer_name'],
        "order_date": form_data['order_date'],
        "status": form_data['status'],
        "shipping_address": form_data['shipping_address'],
        # Preserve existing items or initialize as empty list for new orders
        "items": ORDERS_DATA.get(order_id, {}).get('items', [])
    }
    # Handle numeric fields with type conversion
    new_order_data['total_amount'] = float(form_data.get('total_amount', 0.0))
    new_order_data['amount_paid'] = float(form_data.get('amount_paid', 0.0))

    ORDERS_DATA[order_id] = new_order_data
    save_orders(ORDERS_DATA)
    return redirect(url_for('find_order_get', order_id=order_id))


if __name__ == '__main__':
    # The host='0.0.0.0' makes it accessible from your network
    app.run(host='0.0.0.0', port=5001)