from flask import Flask, request
from flask_cors import CORS
from web3 import Web3
import qrcode
import io
import base64
from datetime import datetime

app = Flask(__name__)
CORS(app)

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
products = {}
stakeholders = {}

@app.route('/')
def home():
    blockchain_status = "Connected" if w3.is_connected() else "Disconnected"
    latest_block = w3.eth.block_number if w3.is_connected() else "N/A"
    account_count = len(w3.eth.accounts) if w3.is_connected() else 0
    
    return f"""
    <html>
    <head><title>AgroLink</title></head>
    <body style="font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); margin: 0; padding: 20px;">
        <div style="max-width: 1000px; margin: 0 auto; background: white; border-radius: 15px; padding: 30px;">
            <h1 style="text-align: center; color: #4CAF50;">🌱 AgroLink</h1>
            <p style="text-align: center; font-size: 18px;">Transparent Agricultural Supply Chain on Blockchain</p>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0;">
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center;">
                    <h3>Blockchain Status</h3>
                    <p><strong>{blockchain_status}</strong></p>
                </div>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center;">
                    <h3>Latest Block</h3>
                    <p><strong>{latest_block}</strong></p>
                </div>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center;">
                    <h3>Available Accounts</h3>
                    <p><strong>{account_count}</strong></p>
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0;">
                <div style="background: #4CAF50; color: white; padding: 30px; border-radius: 10px; text-align: center;">
                    <h3>👨‍🌾 Farmer Portal</h3>
                    <p>Register and add products</p>
                    <a href="/register" style="background: white; color: #4CAF50; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Get Started</a>
                </div>
                <div style="background: #2196F3; color: white; padding: 30px; border-radius: 10px; text-align: center;">
                    <h3>🚚 Add Products</h3>
                    <p>Add new products</p>
                    <a href="/add_product" style="background: white; color: #2196F3; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Add Product</a>
                </div>
                <div style="background: #FF9800; color: white; padding: 30px; border-radius: 10px; text-align: center;">
                    <h3>🏪 View Products</h3>
                    <p>Browse all products</p>
                    <a href="/products" style="background: white; color: #FF9800; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View All</a>
                </div>
                <div style="background: #9C27B0; color: white; padding: 30px; border-radius: 10px; text-align: center;">
                    <h3>📱 Track Product</h3>
                    <p>Track supply chain</p>
                    <a href="/track/1" style="background: white; color: #9C27B0; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Track Demo</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/register')
def register_form():
    return f"""
    <html>
    <head><title>Register - AgroLink</title></head>
    <body style="font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px;">
            <h1 style="color: #4CAF50; text-align: center;">Register</h1>
            <form method="POST">
                <p><label>Name:</label><br>
                <input type="text" name="name" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;" required></p>
                
                <p><label>Type:</label><br>
                <select name="type" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;" required>
                    <option value="">Select type</option>
                    <option value="Farmer">Farmer</option>
                    <option value="Distributor">Distributor</option>
                    <option value="Retailer">Retailer</option>
                    <option value="Consumer">Consumer</option>
                </select></p>
                
                <p><label>Address:</label><br>
                <input type="text" name="address" value="{w3.eth.accounts[0] if w3.eth.accounts else ''}" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;" required></p>
                
                <p style="text-align: center;">
                <button type="submit" style="background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px;">Register</button></p>
            </form>
        </div>
    </body>
    </html>
    """

@app.route('/register', methods=['POST'])
def register_stakeholder():
    data = request.form
    stakeholder_id = len(stakeholders) + 1
    stakeholders[stakeholder_id] = {
        'id': stakeholder_id,
        'name': data['name'],
        'type': data['type'],
        'address': data['address']
    }
    
    return f"""
    <html>
    <body style="font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto; background: #4CAF50; color: white; padding: 30px; border-radius: 15px; text-align: center;">
            <h1>Success!</h1>
            <p>Welcome {data['name']}!</p>
            <p>ID: {stakeholder_id} | Type: {data['type']}</p>
            <a href="/" style="background: white; color: #4CAF50; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Dashboard</a>
        </div>
    </body>
    </html>
    """

@app.route('/add_product')
def add_product_form():
    return f"""
    <html>
    <head><title>Add Product - AgroLink</title></head>
    <body style="font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px;">
            <h1 style="color: #4CAF50; text-align: center;">Add Product</h1>
            <form method="POST">
                <p><label>Product Name:</label><br>
                <input type="text" name="name" placeholder="Organic Tomatoes" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;" required></p>
                
                <p><label>Origin:</label><br>
                <input type="text" name="origin" placeholder="Maharashtra, India" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;" required></p>
                
                <p><label>Price (ETH):</label><br>
                <input type="number" name="price" step="0.01" placeholder="1.0" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;" required></p>
                
                <p><label>Farmer Address:</label><br>
                <input type="text" name="farmer" value="{w3.eth.accounts[1] if len(w3.eth.accounts) > 1 else (w3.eth.accounts[0] if w3.eth.accounts else '')}" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;" required></p>
                
                <p style="text-align: center;">
                <button type="submit" style="background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px;">Add Product</button></p>
            </form>
        </div>
    </body>
    </html>
    """

@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.form
    product_id = len(products) + 1
    
    # Check if the farmer address exists in stakeholders
    farmer_found = False
    farmer_name = "Unknown Farmer"
    farmer_type = "Unknown"
    
    for stakeholder in stakeholders.values():
        if stakeholder['address'] == data['farmer']:
            farmer_found = True
            farmer_name = stakeholder['name']
            farmer_type = stakeholder['type']
            break
    
    # If farmer not found, suggest registration
    if not farmer_found:
        return f"""
        <html>
        <body style="font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background: #FF5722; color: white; padding: 30px; border-radius: 15px; text-align: center;">
                <h1>⚠️ Registration Required</h1>
                <p>The address {data['farmer'][:20]}... is not registered in the system.</p>
                <p><strong>Please register first before adding products.</strong></p>
                <div style="margin: 20px 0;">
                    <a href="/register" style="background: white; color: #FF5722; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px;">Register Now</a>
                    <a href="/add_product" style="background: white; color: #FF5722; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px;">Try Again</a>
                </div>
            </div>
        </body>
        </html>
        """
    
    products[product_id] = {
        'id': product_id,
        'name': data['name'],
        'origin': data['origin'],
        'price': data['price'],
        'farmer': data['farmer'],
        'farmer_name': farmer_name,  # Store the name
        'farmer_type': farmer_type,  # Store the type
        'stage': 'Produced'
    }
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"http://localhost:5000/track/{product_id}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    role_colors = {
        'Farmer': '#4CAF50',
        'Distributor': '#FF9800', 
        'Retailer': '#2196F3',
        'Consumer': '#9C27B0'
    }
    
    role_color = role_colors.get(farmer_type, '#666666')
    
    return f"""
    <html>
    <body style="font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px;">
        <div style="max-width: 500px; margin: 0 auto; background: #4CAF50; color: white; padding: 30px; border-radius: 15px; text-align: center;">
            <h1>Product Added!</h1>
            <p><strong>ID:</strong> {product_id} | <strong>Name:</strong> {data['name']}</p>
            <p><strong>Origin:</strong> {data['origin']} | <strong>Price:</strong> {data['price']} ETH</p>
            <p><strong>Added by:</strong> <span style="color: {role_color}; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 5px;">{farmer_name} ({farmer_type})</span></p>
            <div style="background: white; padding: 15px; border-radius: 10px; margin: 15px 0;">
                <h3 style="color: #333;">QR Code</h3>
                <img src="data:image/png;base64,{qr_code}" alt="QR Code" style="max-width: 150px;">
            </div>
            <a href="/track/{product_id}" style="background: white; color: #4CAF50; padding: 8px 16px; text-decoration: none; border-radius: 5px; margin: 5px;">Track</a>
            <a href="/" style="background: white; color: #4CAF50; padding: 8px 16px; text-decoration: none; border-radius: 5px; margin: 5px;">Home</a>
        </div>
    </body>
    </html>
    """

@app.route('/track/<int:product_id>')
def track_product(product_id):
    if product_id not in products:
        return f"""
        <html>
        <body style="font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; text-align: center;">
                <h1>Product Not Found</h1>
                <p>Product ID {product_id} does not exist</p>
                <a href="/" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Home</a>
            </div>
        </body>
        </html>
        """
    
    product = products[product_id]
    return f"""
    <html>
    <body style="font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px;">
            <h1 style="color: #4CAF50; text-align: center;">Product Tracking</h1>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px;">
                <h3>Product Details:</h3>
                <p><strong>ID:</strong> {product['id']}</p>
                <p><strong>Name:</strong> {product['name']}</p>
                <p><strong>Origin:</strong> {product['origin']}</p>
                <p><strong>Stage:</strong> {product['stage']}</p>
                <p><strong>Price:</strong> {product['price']} ETH</p>
                <p><strong>Farmer:</strong> {product['farmer'][:15]}...</p>
            </div>
            <div style="text-align: center; margin-top: 20px;">
                <a href="/" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Home</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/products')
def view_products():
    if not products:
        return """
        <html>
        <body style="font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px;">
            <div style="max-width: 500px; margin: 0 auto; background: white; padding: 30px; border-radius: 15px; text-align: center;">
                <h1>No Products</h1>
                <p>No products added yet</p>
                <a href="/add_product" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Add Product</a>
            </div>
        </body>
        </html>
        """
    
    products_html = ""
    for product in products.values():
        # Find the stakeholder who added this product
        farmer_info = "Unknown Farmer"
        farmer_type = "Unknown"
        
        for stakeholder in stakeholders.values():
            if stakeholder['address'] == product['farmer']:
                farmer_info = stakeholder['name']
                farmer_type = stakeholder['type']
                break
        
        # Color coding for different roles
        role_colors = {
            'Farmer': '#4CAF50',
            'Distributor': '#FF9800', 
            'Retailer': '#2196F3',
            'Consumer': '#9C27B0'
        }
        
        role_color = role_colors.get(farmer_type, '#666666')
        
        products_html += f"""
        <div style="background: white; padding: 20px; margin: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
            <h3 style="color: #4CAF50;">{product['name']}</h3>
            <p><strong>Product ID:</strong> {product['id']} | <strong>Origin:</strong> {product['origin']}</p>
            <p><strong>Stage:</strong> {product['stage']} | <strong>Price:</strong> {product['price']} ETH</p>
            <p><strong>Added by:</strong> <span style="color: {role_color}; font-weight: bold;">{farmer_info} ({farmer_type})</span></p>
            <p><strong>Farmer Address:</strong> {product['farmer'][:15]}...</p>
            <a href="/track/{product['id']}" style="background: #4CAF50; color: white; padding: 8px 16px; text-decoration: none; border-radius: 5px;">Track</a>
        </div>
        """
    
    return f"""
    <html>
    <body style="font-family: Arial; background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px;">
        <div style="max-width: 800px; margin: 0 auto;">
            <h1 style="color: white; text-align: center;">All Products</h1>
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; margin-bottom: 20px; color: white;">
                <h3>Legend:</h3>
                <p><span style="color: #4CAF50;">● Farmer</span> | <span style="color: #FF9800;">● Distributor</span> | <span style="color: #2196F3;">● Retailer</span> | <span style="color: #9C27B0;">● Consumer</span></p>
            </div>
            {products_html}
            <div style="text-align: center; margin-top: 20px;">
                <a href="/add_product" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px;">Add Product</a>
                <a href="/" style="background: white; color: #4CAF50; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px;">Home</a>
            </div>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("AgroLink Demo Server Starting...")
    print("Blockchain Connected!" if w3.is_connected() else "Blockchain Not Connected!")
    print("Server running at: http://localhost:5000")
    
    if __name__ == '__main__':
        import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)