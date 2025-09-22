from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from datetime import datetime
import json
import os
import hashlib
from PIL import Image, ImageDraw, ImageFont
from werkzeug.utils import secure_filename
import uuid

# Create Flask app
app = Flask(__name__)

# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads/products'
app.config['WATERMARKED_FOLDER'] = 'static/watermarked'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create upload directories
os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)
os.makedirs(os.path.join(app.root_path, app.config['WATERMARKED_FOLDER']), exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_watermark(image_path, farmer_name, output_path):
    """Add farmer name watermark to image"""
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Create a transparent overlay
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Try to use a better font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                try:
                    font = ImageFont.truetype("DejaVuSans.ttf", 40)
                except:
                    font = ImageFont.load_default()
            
            # Watermark text
            watermark_text = f"© {farmer_name} - AgroLink Verified"
            
            # Get text dimensions
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate position (bottom right with some padding)
            x = img.width - text_width - 20
            y = img.height - text_height - 20
            
            # Add semi-transparent background for text
            bg_padding = 10
            draw.rectangle([
                x - bg_padding, 
                y - bg_padding, 
                x + text_width + bg_padding, 
                y + text_height + bg_padding
            ], fill=(0, 0, 0, 120))
            
            # Add the watermark text
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 200))
            
            # Add timestamp watermark in top left
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            timestamp_text = f"Captured: {timestamp}"
            
            # Get timestamp dimensions
            bbox_time = draw.textbbox((0, 0), timestamp_text, font=font)
            time_width = bbox_time[2] - bbox_time[0]
            time_height = bbox_time[3] - bbox_time[1]
            
            # Add timestamp background
            draw.rectangle([
                10, 
                10, 
                10 + time_width + 20, 
                10 + time_height + 20
            ], fill=(0, 0, 0, 120))
            
            # Add timestamp text
            draw.text((20, 20), timestamp_text, font=font, fill=(255, 255, 255, 200))
            
            # Combine the images
            watermarked = Image.alpha_composite(img, overlay)
            
            # Convert back to RGB for JPEG
            if watermarked.mode == 'RGBA':
                watermarked = watermarked.convert('RGB')
            
            # Save the watermarked image
            watermarked.save(output_path, 'JPEG', quality=90)
            
            return True
            
    except Exception as e:
        print(f"Error adding watermark: {str(e)}")
        return False

# Fix CSP issue by adding security headers
@app.after_request
def after_request(response):
    response.headers['Content-Security-Policy'] = "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com; style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; font-src 'self' data:; img-src 'self' data: blob:;"
    return response

# Database simulation (same as before)
class AgroLinkDatabase:
    def __init__(self):
        self.farmers = []
        self.products = []
        self.farmer_counter = 0
        self.product_counter = 0
        self.blockchain_block = 12847
        self.add_sample_data()
    
    def add_sample_data(self):
        sample_farmer = {
            'name': 'Rajesh Kumar',
            'email': 'farmer@example.com',
            'phone': '+91 98765 43210',
            'address': 'Sample Farm, Maharashtra, India',
            'farm_size': '5.0',
            'crops': 'Rice, Wheat, Tomatoes'
        }
        self.add_farmer(sample_farmer)
    
    def add_farmer(self, farmer_data):
        self.farmer_counter += 1
        self.blockchain_block += 1
        
        farmer_data['id'] = self.farmer_counter
        farmer_data['registration_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        farmer_data['blockchain_hash'] = f"0x{self.farmer_counter:08x}ABC123"
        farmer_data['status'] = 'active'
        farmer_data['block_number'] = self.blockchain_block
        
        self.farmers.append(farmer_data)
        print(f"Farmer registered: {farmer_data['name']} (ID: {farmer_data['id']})")
        return farmer_data
    
    def add_product(self, product_data):
        self.product_counter += 1
        self.blockchain_block += 1
        
        hash_input = f"{product_data['product_name']}{product_data['farmer_id']}{datetime.now().isoformat()}"
        blockchain_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        
        product_data['id'] = self.product_counter
        product_data['added_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        product_data['blockchain_hash'] = f"0x{blockchain_hash}"
        product_data['block_number'] = self.blockchain_block
        product_data['status'] = 'active'
        product_data['qr_code'] = f"QR{self.product_counter:06d}"
        
        self.products.append(product_data)
        print(f"Product added: {product_data['product_name']} (ID: {product_data['id']})")
        return product_data
    
    def get_farmer_count(self):
        return len(self.farmers)
    
    def get_product_count(self):
        return len(self.products)
    
    def get_all_farmers(self):
        return self.farmers
    
    def get_all_products(self):
        return self.products
    
    def get_farmer_by_id(self, farmer_id):
        for farmer in self.farmers:
            if farmer['id'] == farmer_id:
                return farmer
        return None
    
    def get_product_by_id(self, product_id):
        for product in self.products:
            if product['id'] == product_id:
                return product
        return None
    
    def get_blockchain_stats(self):
        return {
            'blockchain_status': 'Connected',
            'latest_block': self.blockchain_block,
            'account_count': 8 + self.get_farmer_count(),
            'farmer_count': self.get_farmer_count(),
            'product_count': self.get_product_count()
        }

# Initialize database
db = AgroLinkDatabase()

# Homepage route
@app.route('/')
def index():
    stats = db.get_blockchain_stats()
    return render_template('index.html', 
                         blockchain_status=stats['blockchain_status'],
                         latest_block=stats['latest_block'], 
                         account_count=stats['account_count'])

# Farmer registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    elif request.method == 'POST':
        try:
            farmer_data = {
                'name': request.form.get('name', '').strip(),
                'email': request.form.get('email', '').strip(),
                'phone': request.form.get('phone', '').strip(),
                'address': request.form.get('address', '').strip(),
                'farm_size': request.form.get('farm_size', ''),
                'crops': request.form.get('crops', '').strip()
            }
            
            required_fields = ['name', 'email', 'phone', 'address']
            for field in required_fields:
                if not farmer_data[field]:
                    return jsonify({
                        'success': False,
                        'message': f'{field.replace("_", " ").title()} is required'
                    })
            
            registered_farmer = db.add_farmer(farmer_data)
            
            return jsonify({
                'success': True,
                'message': 'Farmer registered successfully on blockchain!',
                'farmer_id': registered_farmer['id'],
                'blockchain_hash': registered_farmer['blockchain_hash'],
                'registration_date': registered_farmer['registration_date']
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Registration failed: {str(e)}'
            })

# Add product route with image processing
@app.route('/add_product', methods=['GET', 'POST'])  
def add_product():
    if request.method == 'GET':
        stats = db.get_blockchain_stats()
        return render_template('add_product.html',
                             farmer_count=stats['farmer_count'],
                             product_count=stats['product_count'],
                             blockchain_block=stats['latest_block'])
    
    elif request.method == 'POST':
        try:
            product_data = {
                'product_name': request.form.get('product_name', '').strip(),
                'category': request.form.get('category', '').strip(),
                'quantity': request.form.get('quantity', '').strip(),
                'unit': request.form.get('unit', '').strip(),
                'harvest_date': request.form.get('harvest_date', '').strip(),
                'price_per_unit': request.form.get('price_per_unit', '').strip(),
                'farmer_id': request.form.get('farmer_id', '').strip(),
                'farm_location': request.form.get('farm_location', '').strip(),
                'description': request.form.get('description', '').strip()
            }
            
            # Validation
            required_fields = ['product_name', 'category', 'quantity', 'unit', 'harvest_date', 'farmer_id', 'farm_location']
            for field in required_fields:
                if not product_data[field]:
                    return jsonify({
                        'success': False,
                        'message': f'{field.replace("_", " ").title()} is required'
                    })
            
            # Convert and validate farmer_id
            try:
                farmer_id = int(product_data['farmer_id'])
                product_data['farmer_id'] = farmer_id
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid farmer ID'})
            
            # Check if farmer exists
            farmer = db.get_farmer_by_id(farmer_id)
            if not farmer:
                return jsonify({
                    'success': False,
                    'message': f'Farmer with ID {farmer_id} not found. Please register as a farmer first.'
                })
            
            product_data['farmer_name'] = farmer['name']
            
            # Handle image upload and watermarking
            watermarked_filename = None
            if 'product_image' in request.files:
                file = request.files['product_image']
                if file and file.filename != '' and allowed_file(file.filename):
                    # Generate unique filename
                    original_filename = secure_filename(file.filename)
                    file_extension = original_filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                    
                    # Save original image temporarily
                    temp_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(temp_path)
                    
                    # Create watermarked version
                    watermarked_filename = f"watermarked_{unique_filename}"
                    watermarked_path = os.path.join(app.root_path, app.config['WATERMARKED_FOLDER'], watermarked_filename)
                    
                    # Add watermark
                    if add_watermark(temp_path, farmer['name'], watermarked_path):
                        product_data['image_filename'] = watermarked_filename
                        # Remove temporary file
                        os.remove(temp_path)
                    else:
                        return jsonify({'success': False, 'message': 'Failed to process image'})
                elif file and file.filename != '':
                    return jsonify({'success': False, 'message': 'Invalid file type. Please upload JPG, JPEG, or PNG files only.'})
            
            # Add product to blockchain
            added_product = db.add_product(product_data)
            
            return jsonify({
                'success': True,
                'message': 'Product added successfully with watermarked image!',
                'product_id': added_product['id'],
                'blockchain_hash': added_product['blockchain_hash'],
                'block_number': added_product['block_number'],
                'qr_code': added_product['qr_code'],
                'product_count': db.get_product_count(),
                'watermarked_image': watermarked_filename
            })
            
        except Exception as e:
            print(f"Product addition error: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Failed to add product: {str(e)}'
            })

# View products route with watermarked images
@app.route('/products')
def products():
    products_list = db.get_all_products()
    stats = db.get_blockchain_stats()
    
    # Generate products HTML with watermarked images
    products_html = ""
    for product in products_list:        
        # Check if product has watermarked image
        image_html = ""
        if product.get('image_filename'):
            image_html = f"""
            <div style="text-align: center; margin-bottom: 15px;">
                <img src="/watermarked/{product['image_filename']}" 
                     style="max-width: 300px; max-height: 200px; border-radius: 8px; 
                            border: 2px solid rgba(100,217,255,0.3); box-shadow: 0 4px 8px rgba(0,0,0,0.3);"
                     alt="{product['product_name']} - Watermarked by {product['farmer_name']}">
                <p style="font-size: 0.8rem; color: rgba(255,255,255,0.6); margin-top: 5px;">
                    ✅ Watermarked & Verified Image
                </p>
            </div>
            """
        
        products_html += f"""
        <div style="background: rgba(15,15,35,0.25); backdrop-filter: blur(10px); border-radius:16px; 
                    border:1px solid rgba(255,255,255,0.1); box-shadow:0 8px 32px rgba(0,0,0,0.36);
                    padding: 25px; margin-bottom: 20px; transition: all 0.3s ease;
                    border-left: 4px solid #64d9ff;">
            <div style="border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px; margin-bottom: 15px;">
                <h3 style="color: #64d9ff; margin: 0; font-size: 1.4rem; font-weight: 600;">
                    🌾 {product['product_name']}
                </h3>
            </div>
            
            {image_html}
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <div style="background: rgba(138,43,226,0.1); padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="color: #8a2be2; font-size: 0.9rem; margin-bottom: 5px; font-weight: 500;">📅 Harvest Date</div>
                    <div style="color: white; font-size: 1.1rem; font-weight: 600;">{product['harvest_date']}</div>
                </div>
                
                <div style="background: rgba(100,217,255,0.1); padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="color: #64d9ff; font-size: 0.9rem; margin-bottom: 5px; font-weight: 500;">⚖️ Quantity</div>
                    <div style="color: white; font-size: 1.1rem; font-weight: 600;">{product['quantity']} {product['unit']}</div>
                </div>
            </div>
            
            <div style="margin-top: 20px; text-align: center;">
                <button onclick="viewFullImage('{product.get('image_filename', '')}')" 
                        style="background: linear-gradient(45deg, rgba(138,43,226,0.8), rgba(100,217,255,0.8)); 
                               color: white; padding: 10px 20px; border-radius: 8px; border: none; 
                               font-size: 14px; cursor: pointer; margin: 5px; transition: all 0.3s ease;"
                        {"" if product.get('image_filename') else "disabled"}>
                   🖼️ View Watermarked Image
                </button>
            </div>
        </div>
        """
    
    if not products_html:
        products_html = """
        <div style="text-align: center; padding: 50px; background: rgba(255,193,7,0.1); 
                    border: 1px solid rgba(255,193,7,0.3); border-radius: 16px; color: #ffc107;">
            <h3 style="margin-bottom: 15px;">No Products Added Yet</h3>
            <p style="margin-bottom: 20px; color: rgba(255,255,255,0.8);">Be the first farmer to add a watermarked product image!</p>
            <a href="/add_product" style="background: linear-gradient(45deg, rgba(138,43,226,0.8), rgba(100,217,255,0.8));
               color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">
               🚚 Add First Product
            </a>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Products - AgroLink</title>
        <style>
            body {{
                background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #3a1c71);
                background-size: 400% 400%;
                animation: gradientBG 15s ease infinite;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: white;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
            }}
            
            @keyframes gradientBG {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            
            .container {{
                max-width: 1000px;
                margin: 0 auto;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
                padding: 20px 0;
            }}
            
            .header h1 {{
                font-size: 3rem;
                font-weight: bold;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #8a2be2, #64d9ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            
            .stat-card {{
                background: rgba(15,15,35,0.25);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                border: 1px solid rgba(138,43,226,0.3);
                padding: 25px;
                text-align: center;
                transition: all 0.3s ease;
            }}
            
            .nav-buttons {{
                text-align: center;
                margin-bottom: 40px;
            }}
            
            .nav-btn {{
                background: linear-gradient(45deg, rgba(138,43,226,0.8), rgba(100,217,255,0.8));
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                color: white;
                text-decoration: none;
                margin: 0 10px 10px;
                display: inline-block;
                transition: all 0.3s ease;
                font-weight: 600;
            }}
            
            .nav-btn:hover {{
                background: linear-gradient(45deg, rgba(138,43,226,1), rgba(100,217,255,1));
                transform: translateY(-2px);
                color: white;
                text-decoration: none;
            }}
            
            .modal {{
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.8);
            }}
            
            .modal-content {{
                background: rgba(15,15,35,0.9);
                margin: 5% auto;
                padding: 20px;
                border-radius: 16px;
                width: 80%;
                max-width: 600px;
                text-align: center;
            }}
            
            .close {{
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
            }}
            
            .close:hover {{ color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏪 Agricultural Products</h1>
                <p style="font-size: 1.2rem; color: rgba(255,255,255,0.8);">Watermarked & Verified Product Images</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h3 style="color: #64d9ff; margin-bottom: 10px;">Total Products</h3>
                    <p style="font-size: 2.5rem; font-weight: bold; color: white; margin: 0;">{stats['product_count']}</p>
                </div>
                <div class="stat-card">
                    <h3 style="color: #64d9ff; margin-bottom: 10px;">Registered Farmers</h3>
                    <p style="font-size: 2.5rem; font-weight: bold; color: white; margin: 0;">{stats['farmer_count']}</p>
                </div>
                <div class="stat-card">
                    <h3 style="color: #64d9ff; margin-bottom: 10px;">Blockchain Status</h3>
                    <p style="font-size: 1.8rem; font-weight: bold; color: #22c55e; margin: 0;">🟢 Connected</p>
                </div>
            </div>
            
            <div class="nav-buttons">
                <a href="/" class="nav-btn">🏠 Home Dashboard</a>
                <a href="/add_product" class="nav-btn">🚚 Add New Product</a>
                <a href="/register" class="nav-btn">👨‍🌾 Register Farmer</a>
            </div>
            
            <div>
                {products_html}
            </div>
        </div>
        
        <!-- Modal for viewing images -->
        <div id="imageModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal()">&times;</span>
                <h3 style="color: #64d9ff; margin-bottom: 20px;">Watermarked Product Image</h3>
                <img id="modalImage" style="max-width: 100%; max-height: 400px; border-radius: 8px;">
                <p style="margin-top: 15px; color: rgba(255,255,255,0.8);">
                    This image is watermarked with farmer information and timestamp for authenticity verification.
                </p>
            </div>
        </div>
        
        <script>
            function viewFullImage(filename) {{
                if (!filename) return;
                
                const modal = document.getElementById('imageModal');
                const modalImg = document.getElementById('modalImage');
                
                modalImg.src = '/watermarked/' + filename;
                modal.style.display = 'block';
            }}
            
            function closeModal() {{
                document.getElementById('imageModal').style.display = 'none';
            }}
            
            // Close modal when clicking outside
            window.onclick = function(event) {{
                const modal = document.getElementById('imageModal');
                if (event.target == modal) {{
                    modal.style.display = 'none';
                }}
            }}
        </script>
    </body>
    </html>
    """

# Serve watermarked images
@app.route('/watermarked/<filename>')
def watermarked_file(filename):
    return send_from_directory(
        os.path.join(app.root_path, app.config['WATERMARKED_FOLDER']),
        filename
    )

# API Routes (same as before)
@app.route('/api/farmers')
def api_farmers():
    return jsonify({
        'total_farmers': db.get_farmer_count(),
        'farmers': db.get_all_farmers(),
        'blockchain_status': 'Connected',
        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/api/products')
def api_products():
    return jsonify({
        'total_products': db.get_product_count(),
        'products': db.get_all_products(),
        'blockchain_status': 'Connected',
        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/api/stats')
def api_stats():
    return jsonify(db.get_blockchain_stats())

# Run the app
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from datetime import datetime
import json
import os
import hashlib
from PIL import Image, ImageDraw, ImageFont
from werkzeug.utils import secure_filename
import uuid

# Create Flask app
app = Flask(__name__)

# Configuration for file uploads
app.config['UPLOAD_FOLDER'] = 'static/uploads/products'
app.config['WATERMARKED_FOLDER'] = 'static/watermarked'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Create upload directories
os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)
os.makedirs(os.path.join(app.root_path, app.config['WATERMARKED_FOLDER']), exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_watermark(image_path, farmer_name, output_path):
    """Add farmer name watermark to image"""
    try:
        # Open the image
        with Image.open(image_path) as img:
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Create a transparent overlay
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Try to use a better font, fallback to default
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                try:
                    font = ImageFont.truetype("DejaVuSans.ttf", 40)
                except:
                    font = ImageFont.load_default()
            
            # Watermark text
            watermark_text = f"© {farmer_name} - AgroLink Verified"
            
            # Get text dimensions
            bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Calculate position (bottom right with some padding)
            x = img.width - text_width - 20
            y = img.height - text_height - 20
            
            # Add semi-transparent background for text
            bg_padding = 10
            draw.rectangle([
                x - bg_padding, 
                y - bg_padding, 
                x + text_width + bg_padding, 
                y + text_height + bg_padding
            ], fill=(0, 0, 0, 120))
            
            # Add the watermark text
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 200))
            
            # Add timestamp watermark in top left
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            timestamp_text = f"Captured: {timestamp}"
            
            # Get timestamp dimensions
            bbox_time = draw.textbbox((0, 0), timestamp_text, font=font)
            time_width = bbox_time[2] - bbox_time[0]
            time_height = bbox_time[3] - bbox_time[1]
            
            # Add timestamp background
            draw.rectangle([
                10, 
                10, 
                10 + time_width + 20, 
                10 + time_height + 20
            ], fill=(0, 0, 0, 120))
            
            # Add timestamp text
            draw.text((20, 20), timestamp_text, font=font, fill=(255, 255, 255, 200))
            
            # Combine the images
            watermarked = Image.alpha_composite(img, overlay)
            
            # Convert back to RGB for JPEG
            if watermarked.mode == 'RGBA':
                watermarked = watermarked.convert('RGB')
            
            # Save the watermarked image
            watermarked.save(output_path, 'JPEG', quality=90)
            
            return True
            
    except Exception as e:
        print(f"Error adding watermark: {str(e)}")
        return False

# Fix CSP issue by adding security headers
@app.after_request
def after_request(response):
    response.headers['Content-Security-Policy'] = "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com; style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; font-src 'self' data:; img-src 'self' data: blob:;"
    return response

# Database simulation (same as before)
class AgroLinkDatabase:
    def __init__(self):
        self.farmers = []
        self.products = []
        self.farmer_counter = 0
        self.product_counter = 0
        self.blockchain_block = 12847
        self.add_sample_data()
    
    def add_sample_data(self):
        sample_farmer = {
            'name': 'Rajesh Kumar',
            'email': 'farmer@example.com',
            'phone': '+91 98765 43210',
            'address': 'Sample Farm, Maharashtra, India',
            'farm_size': '5.0',
            'crops': 'Rice, Wheat, Tomatoes'
        }
        self.add_farmer(sample_farmer)
    
    def add_farmer(self, farmer_data):
        self.farmer_counter += 1
        self.blockchain_block += 1
        
        farmer_data['id'] = self.farmer_counter
        farmer_data['registration_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        farmer_data['blockchain_hash'] = f"0x{self.farmer_counter:08x}ABC123"
        farmer_data['status'] = 'active'
        farmer_data['block_number'] = self.blockchain_block
        
        self.farmers.append(farmer_data)
        print(f"Farmer registered: {farmer_data['name']} (ID: {farmer_data['id']})")
        return farmer_data
    
    def add_product(self, product_data):
        self.product_counter += 1
        self.blockchain_block += 1
        
        hash_input = f"{product_data['product_name']}{product_data['farmer_id']}{datetime.now().isoformat()}"
        blockchain_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        
        product_data['id'] = self.product_counter
        product_data['added_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        product_data['blockchain_hash'] = f"0x{blockchain_hash}"
        product_data['block_number'] = self.blockchain_block
        product_data['status'] = 'active'
        product_data['qr_code'] = f"QR{self.product_counter:06d}"
        
        self.products.append(product_data)
        print(f"Product added: {product_data['product_name']} (ID: {product_data['id']})")
        return product_data
    
    def get_farmer_count(self):
        return len(self.farmers)
    
    def get_product_count(self):
        return len(self.products)
    
    def get_all_farmers(self):
        return self.farmers
    
    def get_all_products(self):
        return self.products
    
    def get_farmer_by_id(self, farmer_id):
        for farmer in self.farmers:
            if farmer['id'] == farmer_id:
                return farmer
        return None
    
    def get_product_by_id(self, product_id):
        for product in self.products:
            if product['id'] == product_id:
                return product
        return None
    
    def get_blockchain_stats(self):
        return {
            'blockchain_status': 'Connected',
            'latest_block': self.blockchain_block,
            'account_count': 8 + self.get_farmer_count(),
            'farmer_count': self.get_farmer_count(),
            'product_count': self.get_product_count()
        }

# Initialize database
db = AgroLinkDatabase()

# Homepage route
@app.route('/')
def index():
    stats = db.get_blockchain_stats()
    return render_template('index.html', 
                         blockchain_status=stats['blockchain_status'],
                         latest_block=stats['latest_block'], 
                         account_count=stats['account_count'])

# Farmer registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    elif request.method == 'POST':
        try:
            farmer_data = {
                'name': request.form.get('name', '').strip(),
                'email': request.form.get('email', '').strip(),
                'phone': request.form.get('phone', '').strip(),
                'address': request.form.get('address', '').strip(),
                'farm_size': request.form.get('farm_size', ''),
                'crops': request.form.get('crops', '').strip()
            }
            
            required_fields = ['name', 'email', 'phone', 'address']
            for field in required_fields:
                if not farmer_data[field]:
                    return jsonify({
                        'success': False,
                        'message': f'{field.replace("_", " ").title()} is required'
                    })
            
            registered_farmer = db.add_farmer(farmer_data)
            
            return jsonify({
                'success': True,
                'message': 'Farmer registered successfully on blockchain!',
                'farmer_id': registered_farmer['id'],
                'blockchain_hash': registered_farmer['blockchain_hash'],
                'registration_date': registered_farmer['registration_date']
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Registration failed: {str(e)}'
            })

# Add product route with image processing
@app.route('/add_product', methods=['GET', 'POST'])  
def add_product():
    if request.method == 'GET':
        stats = db.get_blockchain_stats()
        return render_template('add_product.html',
                             farmer_count=stats['farmer_count'],
                             product_count=stats['product_count'],
                             blockchain_block=stats['latest_block'])
    
    elif request.method == 'POST':
        try:
            product_data = {
                'product_name': request.form.get('product_name', '').strip(),
                'category': request.form.get('category', '').strip(),
                'quantity': request.form.get('quantity', '').strip(),
                'unit': request.form.get('unit', '').strip(),
                'harvest_date': request.form.get('harvest_date', '').strip(),
                'price_per_unit': request.form.get('price_per_unit', '').strip(),
                'farmer_id': request.form.get('farmer_id', '').strip(),
                'farm_location': request.form.get('farm_location', '').strip(),
                'description': request.form.get('description', '').strip()
            }
            
            # Validation
            required_fields = ['product_name', 'category', 'quantity', 'unit', 'harvest_date', 'farmer_id', 'farm_location']
            for field in required_fields:
                if not product_data[field]:
                    return jsonify({
                        'success': False,
                        'message': f'{field.replace("_", " ").title()} is required'
                    })
            
            # Convert and validate farmer_id
            try:
                farmer_id = int(product_data['farmer_id'])
                product_data['farmer_id'] = farmer_id
            except ValueError:
                return jsonify({'success': False, 'message': 'Invalid farmer ID'})
            
            # Check if farmer exists
            farmer = db.get_farmer_by_id(farmer_id)
            if not farmer:
                return jsonify({
                    'success': False,
                    'message': f'Farmer with ID {farmer_id} not found. Please register as a farmer first.'
                })
            
            product_data['farmer_name'] = farmer['name']
            
            # Handle image upload and watermarking
            watermarked_filename = None
            if 'product_image' in request.files:
                file = request.files['product_image']
                if file and file.filename != '' and allowed_file(file.filename):
                    # Generate unique filename
                    original_filename = secure_filename(file.filename)
                    file_extension = original_filename.rsplit('.', 1)[1].lower()
                    unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
                    
                    # Save original image temporarily
                    temp_path = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(temp_path)
                    
                    # Create watermarked version
                    watermarked_filename = f"watermarked_{unique_filename}"
                    watermarked_path = os.path.join(app.root_path, app.config['WATERMARKED_FOLDER'], watermarked_filename)
                    
                    # Add watermark
                    if add_watermark(temp_path, farmer['name'], watermarked_path):
                        product_data['image_filename'] = watermarked_filename
                        # Remove temporary file
                        os.remove(temp_path)
                    else:
                        return jsonify({'success': False, 'message': 'Failed to process image'})
                elif file and file.filename != '':
                    return jsonify({'success': False, 'message': 'Invalid file type. Please upload JPG, JPEG, or PNG files only.'})
            
            # Add product to blockchain
            added_product = db.add_product(product_data)
            
            return jsonify({
                'success': True,
                'message': 'Product added successfully with watermarked image!',
                'product_id': added_product['id'],
                'blockchain_hash': added_product['blockchain_hash'],
                'block_number': added_product['block_number'],
                'qr_code': added_product['qr_code'],
                'product_count': db.get_product_count(),
                'watermarked_image': watermarked_filename
            })
            
        except Exception as e:
            print(f"Product addition error: {str(e)}")
            return jsonify({
                'success': False,
                'message': f'Failed to add product: {str(e)}'
            })

# View products route with watermarked images
@app.route('/products')
def products():
    products_list = db.get_all_products()
    stats = db.get_blockchain_stats()
    
    # Generate products HTML with watermarked images
    products_html = ""
    for product in products_list:        
        # Check if product has watermarked image
        image_html = ""
        if product.get('image_filename'):
            image_html = f"""
            <div style="text-align: center; margin-bottom: 15px;">
                <img src="/watermarked/{product['image_filename']}" 
                     style="max-width: 300px; max-height: 200px; border-radius: 8px; 
                            border: 2px solid rgba(100,217,255,0.3); box-shadow: 0 4px 8px rgba(0,0,0,0.3);"
                     alt="{product['product_name']} - Watermarked by {product['farmer_name']}">
                <p style="font-size: 0.8rem; color: rgba(255,255,255,0.6); margin-top: 5px;">
                    ✅ Watermarked & Verified Image
                </p>
            </div>
            """
        
        products_html += f"""
        <div style="background: rgba(15,15,35,0.25); backdrop-filter: blur(10px); border-radius:16px; 
                    border:1px solid rgba(255,255,255,0.1); box-shadow:0 8px 32px rgba(0,0,0,0.36);
                    padding: 25px; margin-bottom: 20px; transition: all 0.3s ease;
                    border-left: 4px solid #64d9ff;">
            <div style="border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px; margin-bottom: 15px;">
                <h3 style="color: #64d9ff; margin: 0; font-size: 1.4rem; font-weight: 600;">
                    🌾 {product['product_name']}
                </h3>
            </div>
            
            {image_html}
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <div style="background: rgba(138,43,226,0.1); padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="color: #8a2be2; font-size: 0.9rem; margin-bottom: 5px; font-weight: 500;">📅 Harvest Date</div>
                    <div style="color: white; font-size: 1.1rem; font-weight: 600;">{product['harvest_date']}</div>
                </div>
                
                <div style="background: rgba(100,217,255,0.1); padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="color: #64d9ff; font-size: 0.9rem; margin-bottom: 5px; font-weight: 500;">⚖️ Quantity</div>
                    <div style="color: white; font-size: 1.1rem; font-weight: 600;">{product['quantity']} {product['unit']}</div>
                </div>
            </div>
            
            <div style="margin-top: 20px; text-align: center;">
                <button onclick="viewFullImage('{product.get('image_filename', '')}')" 
                        style="background: linear-gradient(45deg, rgba(138,43,226,0.8), rgba(100,217,255,0.8)); 
                               color: white; padding: 10px 20px; border-radius: 8px; border: none; 
                               font-size: 14px; cursor: pointer; margin: 5px; transition: all 0.3s ease;"
                        {"" if product.get('image_filename') else "disabled"}>
                   🖼️ View Watermarked Image
                </button>
            </div>
        </div>
        """
    
    if not products_html:
        products_html = """
        <div style="text-align: center; padding: 50px; background: rgba(255,193,7,0.1); 
                    border: 1px solid rgba(255,193,7,0.3); border-radius: 16px; color: #ffc107;">
            <h3 style="margin-bottom: 15px;">No Products Added Yet</h3>
            <p style="margin-bottom: 20px; color: rgba(255,255,255,0.8);">Be the first farmer to add a watermarked product image!</p>
            <a href="/add_product" style="background: linear-gradient(45deg, rgba(138,43,226,0.8), rgba(100,217,255,0.8));
               color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600;">
               🚚 Add First Product
            </a>
        </div>
        """
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Products - AgroLink</title>
        <style>
            body {{
                background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #3a1c71);
                background-size: 400% 400%;
                animation: gradientBG 15s ease infinite;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: white;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
            }}
            
            @keyframes gradientBG {{
                0% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
                100% {{ background-position: 0% 50%; }}
            }}
            
            .container {{
                max-width: 1000px;
                margin: 0 auto;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
                padding: 20px 0;
            }}
            
            .header h1 {{
                font-size: 3rem;
                font-weight: bold;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #8a2be2, #64d9ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }}
            
            .stats {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            
            .stat-card {{
                background: rgba(15,15,35,0.25);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                border: 1px solid rgba(138,43,226,0.3);
                padding: 25px;
                text-align: center;
                transition: all 0.3s ease;
            }}
            
            .nav-buttons {{
                text-align: center;
                margin-bottom: 40px;
            }}
            
            .nav-btn {{
                background: linear-gradient(45deg, rgba(138,43,226,0.8), rgba(100,217,255,0.8));
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                color: white;
                text-decoration: none;
                margin: 0 10px 10px;
                display: inline-block;
                transition: all 0.3s ease;
                font-weight: 600;
            }}
            
            .nav-btn:hover {{
                background: linear-gradient(45deg, rgba(138,43,226,1), rgba(100,217,255,1));
                transform: translateY(-2px);
                color: white;
                text-decoration: none;
            }}
            
            .modal {{
                display: none;
                position: fixed;
                z-index: 1000;
                left: 0;
                top: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.8);
            }}
            
            .modal-content {{
                background: rgba(15,15,35,0.9);
                margin: 5% auto;
                padding: 20px;
                border-radius: 16px;
                width: 80%;
                max-width: 600px;
                text-align: center;
            }}
            
            .close {{
                color: #aaa;
                float: right;
                font-size: 28px;
                font-weight: bold;
                cursor: pointer;
            }}
            
            .close:hover {{ color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏪 Agricultural Products</h1>
                <p style="font-size: 1.2rem; color: rgba(255,255,255,0.8);">Watermarked & Verified Product Images</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h3 style="color: #64d9ff; margin-bottom: 10px;">Total Products</h3>
                    <p style="font-size: 2.5rem; font-weight: bold; color: white; margin: 0;">{stats['product_count']}</p>
                </div>
                <div class="stat-card">
                    <h3 style="color: #64d9ff; margin-bottom: 10px;">Registered Farmers</h3>
                    <p style="font-size: 2.5rem; font-weight: bold; color: white; margin: 0;">{stats['farmer_count']}</p>
                </div>
                <div class="stat-card">
                    <h3 style="color: #64d9ff; margin-bottom: 10px;">Blockchain Status</h3>
                    <p style="font-size: 1.8rem; font-weight: bold; color: #22c55e; margin: 0;">🟢 Connected</p>
                </div>
            </div>
            
            <div class="nav-buttons">
                <a href="/" class="nav-btn">🏠 Home Dashboard</a>
                <a href="/add_product" class="nav-btn">🚚 Add New Product</a>
                <a href="/register" class="nav-btn">👨‍🌾 Register Farmer</a>
            </div>
            
            <div>
                {products_html}
            </div>
        </div>
        
        <!-- Modal for viewing images -->
        <div id="imageModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal()">&times;</span>
                <h3 style="color: #64d9ff; margin-bottom: 20px;">Watermarked Product Image</h3>
                <img id="modalImage" style="max-width: 100%; max-height: 400px; border-radius: 8px;">
                <p style="margin-top: 15px; color: rgba(255,255,255,0.8);">
                    This image is watermarked with farmer information and timestamp for authenticity verification.
                </p>
            </div>
        </div>
        
        <script>
            function viewFullImage(filename) {{
                if (!filename) return;
                
                const modal = document.getElementById('imageModal');
                const modalImg = document.getElementById('modalImage');
                
                modalImg.src = '/watermarked/' + filename;
                modal.style.display = 'block';
            }}
            
            function closeModal() {{
                document.getElementById('imageModal').style.display = 'none';
            }}
            
            // Close modal when clicking outside
            window.onclick = function(event) {{
                const modal = document.getElementById('imageModal');
                if (event.target == modal) {{
                    modal.style.display = 'none';
                }}
            }}
        </script>
    </body>
    </html>
    """

# Serve watermarked images
@app.route('/watermarked/<filename>')
def watermarked_file(filename):
    return send_from_directory(
        os.path.join(app.root_path, app.config['WATERMARKED_FOLDER']),
        filename
    )

# API Routes (same as before)
@app.route('/api/farmers')
def api_farmers():
    return jsonify({
        'total_farmers': db.get_farmer_count(),
        'farmers': db.get_all_farmers(),
        'blockchain_status': 'Connected',
        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/api/products')
def api_products():
    return jsonify({
        'total_products': db.get_product_count(),
        'products': db.get_all_products(),
        'blockchain_status': 'Connected',
        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/api/stats')
def api_stats():
    return jsonify(db.get_blockchain_stats())

# Run the app
if __name__ == '__main__':
    print("🚀 Starting AgroLink with Image Watermarking...")
    print("=" * 60)
    print("🌐 Dashboard: https://bachhavr788-pixel.github.io/register")
    print("👨‍🌾 Register Farmer: http://localhost:5000/register")
    print("🚚 Add Products: http://localhost:5000/add_product")
    print("🏪 View Products: http://localhost:5000/products")
    print("📊 APIs: /api/farmers, /api/products, /api/stats")
    print("=" * 60)
    print("✅ Image watermarking system ready!")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)