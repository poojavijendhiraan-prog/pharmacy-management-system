from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pharmacy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/medicines')
def medicines():
    return render_template('medicines.html')

@app.route('/sales')
def sales():
    return render_template('sales.html')

@app.route('/inventory')
def inventory():
    return render_template('inventory.html')

@app.route('/api/medicines', methods=['GET'])
def get_medicines():
    medicines = Medicine.query.all()
    return jsonify([{
        'id': m.id,
        'name': m.name,
        'quantity': m.quantity,
        'price': m.price
    } for m in medicines])

@app.route('/api/medicines', methods=['POST'])
def add_medicine():
    data = request.json
    medicine = Medicine(
        name=data['name'],
        quantity=data['quantity'],
        price=data['price']
    )
    db.session.add(medicine)
    db.session.commit()
    return jsonify({'message': 'Medicine added successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)