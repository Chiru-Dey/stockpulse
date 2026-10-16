from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models import Category
from app.utils import admin_required

categories_bp = Blueprint("categories", __name__, url_prefix="/api/categories")

@categories_bp.get("")
@jwt_required()
def get_categories():
    search = request.args.get("search", "").strip()
    
    query = Category.query
    if search:
        query = query.filter(Category.name.ilike(f"%{search}%"))
        
    categories = query.order_by(Category.name).all()
    
    return jsonify({
        "categories": [cat.to_dict() for cat in categories]
    }), 200

@categories_bp.get("/<int:category_id>")
@jwt_required()
def get_category(category_id):
    category = Category.query.get_or_404(category_id)
    return jsonify(category.to_dict()), 200

@categories_bp.post("")
@admin_required()
def create_category():
    data = request.get_json()
    if not data or not data.get("name"):
        return jsonify({"error": "Category name is required"}), 400
        
    name = data["name"].strip()
    
    if Category.query.filter_by(name=name).first():
        return jsonify({"error": "Category already exists"}), 409
        
    category = Category(name=name, description=data.get("description"))
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify(category.to_dict()), 201

@categories_bp.patch("/<int:category_id>")
@admin_required()
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
        
    if "name" in data:
        new_name = data["name"].strip()
        existing = Category.query.filter(Category.name == new_name, Category.id != category_id).first()
        if existing:
            return jsonify({"error": "Category name already in use"}), 409
        category.name = new_name
        
    if "description" in data:
        category.description = data["description"]
        
    db.session.commit()
    
    return jsonify(category.to_dict()), 200

@categories_bp.delete("/<int:category_id>")
@admin_required()
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    if category.products.count() > 0:
        return jsonify({"error": "Cannot delete category with existing products"}), 400
        
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({"message": "Category deleted"}), 200