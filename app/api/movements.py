from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.extensions import db
from app.models import StockMovement, Product

movements_bp = Blueprint("movements", __name__, url_prefix="/api/stock-movements")

@movements_bp.get("")
@jwt_required()
def get_movements():
    product_id = request.args.get("product_id", type=int)
    movement_type = request.args.get("movement_type", "").strip().upper()
    date_from = request.args.get("date_from")
    date_to = request.args.get("date_to")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    
    query = StockMovement.query
    
    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
        
    if movement_type in ["IN", "OUT"]:
        query = query.filter(StockMovement.movement_type == movement_type)
        
    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from)
            query = query.filter(StockMovement.created_at >= dt_from)
        except ValueError:
            pass
            
    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to)
            query = query.filter(StockMovement.created_at <= dt_to)
        except ValueError:
            pass
            
    pagination = query.order_by(StockMovement.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        "movements": [m.to_dict() for m in pagination.items],
        "total": pagination.total,
        "page": page,
        "per_page": per_page,
        "pages": pagination.pages
    }), 200

@movements_bp.get("/<int:movement_id>")
@jwt_required()
def get_movement(movement_id):
    movement = StockMovement.query.get_or_404(movement_id)
    return jsonify(movement.to_dict()), 200

@movements_bp.post("")
@jwt_required()
def create_movement():
    data = request.get_json()
    
    if not data or not data.get("product_id") or not data.get("movement_type") or not data.get("quantity"):
        return jsonify({"error": "product_id, movement_type, and quantity are required"}), 400
        
    product_id = data["product_id"]
    movement_type = data["movement_type"].strip().upper()
    quantity = data["quantity"]
    note = data.get("note", "")
    
    if movement_type not in ["IN", "OUT"]:
        return jsonify({"error": "movement_type must be IN or OUT"}), 400
        
    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "quantity must be a positive integer"}), 400
        
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
        
    # Validate OUT movements against current stock
    if movement_type == "OUT":
        current_stock = product.current_stock
        if quantity > current_stock:
            return jsonify({
                "error": "Insufficient stock", 
                "current_stock": current_stock
            }), 400
            
    # Get current user ID from JWT
    user_id = int(get_jwt_identity())
    
    movement = StockMovement(
        product_id=product_id,
        movement_type=movement_type,
        quantity=quantity,
        note=note,
        created_by=user_id
    )
    
    db.session.add(movement)
    db.session.commit()
    
    return jsonify(movement.to_dict()), 201