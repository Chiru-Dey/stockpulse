from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Product, Category
from app.utils import admin_required

products_bp = Blueprint("products", __name__, url_prefix="/api/products")

@products_bp.get("")
@jwt_required()
def get_products():
    search = request.args.get("search", "").strip()
    category_id = request.args.get("category_id", type=int)
    stock_status = request.args.get("stock_status", "").strip().lower()
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    
    query = Product.query
    
    # Filter by search string (name or SKU)
    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%")
            )
        )
        
    # Filter by category
    if category_id:
        query = query.filter(Product.category_id == category_id)
        
    # Filter by stock status
    # Because stock_status is a Python property calculated on the fly, 
    # we fetch the records and filter them in memory before paginating.
    if stock_status in ["ok", "low", "out"]:
        all_products = query.order_by(Product.name).all()
        filtered_products = [p for p in all_products if p.stock_status == stock_status]
        total = len(filtered_products)
        start = (page - 1) * per_page
        end = start + per_page
        products = filtered_products[start:end]
    else:
        pagination = query.order_by(Product.name).paginate(
            page=page, per_page=per_page, error_out=False
        )
        products = pagination.items
        total = pagination.total

    return jsonify({
        "products": [p.to_dict() for p in products],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page if per_page > 0 else 0
    }), 200

@products_bp.get("/<int:product_id>")
@jwt_required()
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200

@products_bp.post("")
@admin_required()
def create_product():
    data = request.get_json()
    if not data or not data.get("name") or not data.get("sku"):
        return jsonify({"error": "Name and SKU are required"}), 400
        
    name = data["name"].strip()
    sku = data["sku"].strip()
    
    if Product.query.filter_by(sku=sku).first():
        return jsonify({"error": "SKU already exists"}), 409
        
    category_id = data.get("category_id")
    if category_id and not Category.query.get(category_id):
        return jsonify({"error": "Category not found"}), 404
            
    product = Product(
        name=name,
        sku=sku,
        description=data.get("description"),
        category_id=category_id,
        low_stock_threshold=data.get("low_stock_threshold", 10)
    )
    
    db.session.add(product)
    db.session.commit()
    
    return jsonify(product.to_dict()), 201

@products_bp.patch("/<int:product_id>")
@admin_required()
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    if "name" in data:
        product.name = data["name"].strip()
        
    if "sku" in data:
        new_sku = data["sku"].strip()
        existing = Product.query.filter(Product.sku == new_sku, Product.id != product_id).first()
        if existing:
            return jsonify({"error": "SKU already in use"}), 409
        product.sku = new_sku
        
    if "description" in data:
        product.description = data["description"]
        
    if "category_id" in data:
        if data["category_id"] and not Category.query.get(data["category_id"]):
            return jsonify({"error": "Category not found"}), 404
        product.category_id = data["category_id"]
        
    if "low_stock_threshold" in data:
        product.low_stock_threshold = data["low_stock_threshold"]
        
    db.session.commit()
    
    return jsonify(product.to_dict()), 200

@products_bp.delete("/<int:product_id>")
@admin_required()
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    
    # Note: Our model cascade="all, delete-orphan" will automatically 
    # delete associated stock movements when the product is deleted.
    db.session.delete(product)
    db.session.commit()
    
    return jsonify({"message": "Product deleted"}), 200