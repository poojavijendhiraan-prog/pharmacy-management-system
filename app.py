from flask import Flask, render_template, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pharmacy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)  # Enable CORS for API calls

# Models
class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'price': self.price,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicine.id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    date_sold = db.Column(db.DateTime, default=datetime.utcnow)
    
    medicine = db.relationship('Medicine', backref='sales')
    
    def to_dict(self):
        return {
            'id': self.id,
            'medicine_id': self.medicine_id,
            'medicine_name': self.medicine.name if self.medicine else 'Unknown',
            'quantity_sold': self.quantity_sold,
            'total_price': self.total_price,
            'date_sold': self.date_sold.isoformat() if self.date_sold else None
        }

# Routes
@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Template error: {e}")
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pharmacy Management System</title>
            <link rel="stylesheet" href="/static/css/style.css">
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>Pharmacy Management System</h1>
                    <nav>
                        <ul>
                            <li><a href="/" class="active">Dashboard</a></li>
                            <li><a href="/medicines">Medicines</a></li>
                            <li><a href="/sales">Sales</a></li>
                            <li><a href="/inventory">Inventory</a></li>
                        </ul>
                    </nav>
                </header>
                <main>
                    <div class="dashboard">
                        <div class="card">
                            <h2>Quick Stats</h2>
                            <div class="stats">
                                <div class="stat-item">
                                    <h3>Total Medicines</h3>
                                    <p id="total-medicines">0</p>
                                </div>
                                <div class="stat-item">
                                    <h3>Low Stock Items</h3>
                                    <p id="low-stock">0</p>
                                </div>
                                <div class="stat-item">
                                    <h3>Total Value</h3>
                                    <p id="total-value">$0.00</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </main>
                <footer>
                    <p>&copy; 2025 Pharmacy Management System</p>
                </footer>
            </div>
            <script src="/static/js/main.js"></script>
        </body>
        </html>
        '''

@app.route('/medicines')
def medicines():
    try:
        return render_template('medicines.html')
    except Exception as e:
        print(f"Template error: {e}")
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Medicines - Pharmacy Management System</title>
            <link rel="stylesheet" href="/static/css/style.css">
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>Pharmacy Management System</h1>
                    <nav>
                        <ul>
                            <li><a href="/">Dashboard</a></li>
                            <li><a href="/medicines" class="active">Medicines</a></li>
                            <li><a href="/sales">Sales</a></li>
                            <li><a href="/inventory">Inventory</a></li>
                        </ul>
                    </nav>
                </header>
                <main>
                    <div class="dashboard">
                        <div class="card">
                            <h2>Add New Medicine</h2>
                            <form id="add-medicine-form">
                                <input type="text" name="name" placeholder="Medicine Name" required>
                                <input type="number" name="quantity" placeholder="Quantity" min="0" required>
                                <input type="number" name="price" placeholder="Price" step="0.01" min="0" required>
                                <button type="submit">Add Medicine</button>
                            </form>
                        </div>
                        <div class="card">
                            <h2>All Medicines</h2>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Name</th>
                                        <th>Quantity</th>
                                        <th>Price</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="medicines-body">
                                    <!-- Medicines will be loaded here -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </main>
                <footer>
                    <p>&copy; 2025 Pharmacy Management System</p>
                </footer>
            </div>
            <script src="/static/js/main.js"></script>
        </body>
        </html>
        '''

@app.route('/sales')
def sales():
    try:
        return render_template('sales.html')
    except Exception as e:
        print(f"Template error: {e}")
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sales - Pharmacy Management System</title>
            <link rel="stylesheet" href="/static/css/style.css">
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>Pharmacy Management System</h1>
                    <nav>
                        <ul>
                            <li><a href="/">Dashboard</a></li>
                            <li><a href="/medicines">Medicines</a></li>
                            <li><a href="/sales" class="active">Sales</a></li>
                            <li><a href="/inventory">Inventory</a></li>
                        </ul>
                    </nav>
                </header>
                <main>
                    <div class="dashboard">
                        <div class="card">
                            <h2>Make a Sale</h2>
                            <form id="make-sale-form">
                                <select name="medicine_id" id="medicine-select" required>
                                    <option value="">Select Medicine</option>
                                </select>
                                <input type="number" name="quantity" placeholder="Quantity to Sell" min="1" required>
                                <button type="submit">Complete Sale</button>
                            </form>
                        </div>
                        <div class="card">
                            <h2>Sales History</h2>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Medicine</th>
                                        <th>Quantity Sold</th>
                                        <th>Total Price</th>
                                        <th>Date</th>
                                    </tr>
                                </thead>
                                <tbody id="sales-body">
                                    <!-- Sales will be loaded here -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </main>
                <footer>
                    <p>&copy; 2025 Pharmacy Management System</p>
                </footer>
            </div>
            <script src="/static/js/main.js"></script>
        </body>
        </html>
        '''

@app.route('/inventory')
def inventory():
    try:
        return render_template('inventory.html')
    except Exception as e:
        print(f"Template error: {e}")
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Inventory - Pharmacy Management System</title>
            <link rel="stylesheet" href="/static/css/style.css">
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>Pharmacy Management System</h1>
                    <nav>
                        <ul>
                            <li><a href="/">Dashboard</a></li>
                            <li><a href="/medicines">Medicines</a></li>
                            <li><a href="/sales">Sales</a></li>
                            <li><a href="/inventory" class="active">Inventory</a></li>
                        </ul>
                    </nav>
                </header>
                <main>
                    <div class="dashboard">
                        <div class="card">
                            <h2>Low Stock Items</h2>
                            <div id="low-stock-items" class="inventory-grid">
                                <!-- Low stock items will be loaded here -->
                            </div>
                        </div>
                        <div class="card">
                            <h2>Out of Stock Items</h2>
                            <div id="out-of-stock-items" class="inventory-grid">
                                <!-- Out of stock items will be loaded here -->
                            </div>
                        </div>
                    </div>
                </main>
                <footer>
                    <p>&copy; 2025 Pharmacy Management System</p>
                </footer>
            </div>
            <script src="/static/js/main.js"></script>
        </body>
        </html>
        '''

# API Routes
@app.route('/api/medicines', methods=['GET'])
def get_medicines():
    try:
        medicines = Medicine.query.all()
        return jsonify([medicine.to_dict() for medicine in medicines])
    except Exception as e:
        print(f"Error getting medicines: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/medicines', methods=['POST'])
def add_medicine():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['name', 'quantity', 'price']):
            return jsonify({'error': 'Missing required fields: name, quantity, price'}), 400
            
        # Validate data types
        try:
            quantity = int(data['quantity'])
            price = float(data['price'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid data types for quantity or price'}), 400
            
        # Validate values
        if quantity < 0 or price < 0:
            return jsonify({'error': 'Quantity and price must be non-negative'}), 400
            
        medicine = Medicine(
            name=data['name'].strip(),
            quantity=quantity,
            price=price
        )
        
        db.session.add(medicine)
        db.session.commit()
        
        return jsonify({
            'message': 'Medicine added successfully', 
            'id': medicine.id,
            'medicine': medicine.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error adding medicine: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/medicines/<int:medicine_id>', methods=['PUT'])
def update_medicine(medicine_id):
    try:
        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            return jsonify({'error': 'Medicine not found'}), 404
            
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields if provided
        if 'name' in data:
            medicine.name = data['name'].strip()
        if 'quantity' in data:
            try:
                quantity = int(data['quantity'])
                if quantity < 0:
                    return jsonify({'error': 'Quantity must be non-negative'}), 400
                medicine.quantity = quantity
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid quantity value'}), 400
                
        if 'price' in data:
            try:
                price = float(data['price'])
                if price < 0:
                    return jsonify({'error': 'Price must be non-negative'}), 400
                medicine.price = price
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid price value'}), 400
            
        db.session.commit()
        return jsonify({
            'message': 'Medicine updated successfully',
            'medicine': medicine.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error updating medicine: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/medicines/<int:medicine_id>', methods=['DELETE'])
def delete_medicine(medicine_id):
    try:
        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            return jsonify({'error': 'Medicine not found'}), 404
            
        # Check if medicine has sales history
        if medicine.sales:
            return jsonify({'error': 'Cannot delete medicine with sales history'}), 400
            
        db.session.delete(medicine)
        db.session.commit()
        
        return jsonify({'message': 'Medicine deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting medicine: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sales', methods=['GET'])
def get_sales():
    try:
        sales = Sale.query.order_by(Sale.date_sold.desc()).all()
        return jsonify([sale.to_dict() for sale in sales])
    except Exception as e:
        print(f"Error getting sales: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sales', methods=['POST'])
def add_sale():
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['medicine_id', 'quantity_sold']):
            return jsonify({'error': 'Missing required fields: medicine_id, quantity_sold'}), 400
        
        try:
            medicine_id = int(data['medicine_id'])
            quantity_sold = int(data['quantity_sold'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid data types'}), 400
            
        if quantity_sold <= 0:
            return jsonify({'error': 'Quantity sold must be positive'}), 400
            
        medicine = Medicine.query.get(medicine_id)
        if not medicine:
            return jsonify({'error': 'Medicine not found'}), 404
        
        if medicine.quantity < quantity_sold:
            return jsonify({'error': f'Insufficient stock. Available: {medicine.quantity}'}), 400
            
        total_price = medicine.price * quantity_sold
        
        # Create sale record
        sale = Sale(
            medicine_id=medicine.id,
            quantity_sold=quantity_sold,
            total_price=total_price
        )
        
        # Update medicine quantity
        medicine.quantity -= quantity_sold
        
        db.session.add(sale)
        db.session.commit()
        
        return jsonify({
            'message': 'Sale recorded successfully',
            'sale': sale.to_dict(),
            'remaining_stock': medicine.quantity
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error adding sale: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_stats():
    try:
        medicines = Medicine.query.all()
        sales = Sale.query.all()
        
        total_medicines = len(medicines)
        low_stock_items = len([m for m in medicines if m.quantity < 10])
        out_of_stock_items = len([m for m in medicines if m.quantity == 0])
        total_value = sum(m.quantity * m.price for m in medicines)
        total_sales = sum(s.total_price for s in sales)
        
        return jsonify({
            'total_medicines': total_medicines,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'total_value': round(total_value, 2),
            'total_sales': round(total_sales, 2)
        })
        
    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

# Initialize database and add sample data
def init_database():
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("Database tables created successfully")
            
            # Add sample data if database is empty
            if Medicine.query.count() == 0:
                sample_medicines = [
                    Medicine(name='Aspirin', quantity=100, price=5.99),
                    Medicine(name='Paracetamol', quantity=50, price=3.50),
                    Medicine(name='Ibuprofen', quantity=75, price=7.25),
                    Medicine(name='Amoxicillin', quantity=30, price=12.99),
                    Medicine(name='Vitamin C', quantity=8, price=15.50),  # Low stock
                    Medicine(name='Cough Syrup', quantity=0, price=8.75),  # Out of stock
                ]
                
                for medicine in sample_medicines:
                    db.session.add(medicine)
                    
                db.session.commit()
                print("Sample data added to database")
                
                # Add sample sales
                sample_sales = [
                    Sale(medicine_id=1, quantity_sold=5, total_price=29.95),
                    Sale(medicine_id=2, quantity_sold=10, total_price=35.00),
                ]
                
                for sale in sample_sales:
                    db.session.add(sale)
                    
                db.session.commit()
                print("Sample sales data added")
            else:
                print("Database already contains data")
                
        except Exception as e:
            print(f"Error initializing database: {e}")
            db.session.rollback()

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Initialize database
    init_database()
    
    print("Starting Pharmacy Management System...")
    print("Dashboard: http://localhost:5000/")
    print("Medicines: http://localhost:5000/medicines")
    print("Sales: http://localhost:5000/sales")
    print("Inventory: http://localhost:5000/inventory")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
