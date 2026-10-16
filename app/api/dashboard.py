from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.models import Category, Product, StockMovement

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

@dashboard_bp.get("/summary")
@jwt_required()
def get_summary():
    # Category stats
    total_categories = Category.query.count()
    
    # Product & Stock stats
    products = Product.query.all()
    total_products = len(products)
    total_stock_units = 0
    low_stock_count = 0
    out_of_stock_count = 0
    
    for p in products:
        stock = p.current_stock
        total_stock_units += stock
        if stock <= 0:
            out_of_stock_count += 1
        elif stock <= p.low_stock_threshold:
            low_stock_count += 1
            
    # Recent Activity
    recent_movements = StockMovement.query.order_by(
        StockMovement.created_at.desc()
    ).limit(5).all()
    
    return jsonify({
        "total_categories": total_categories,
        "total_products": total_products,
        "total_stock_units": total_stock_units,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "recent_movements": [m.to_dict() for m in recent_movements]
    }), 200