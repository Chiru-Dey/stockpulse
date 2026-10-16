from datetime import datetime, timezone
from sqlalchemy import CheckConstraint
from app.extensions import db
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

def utcnow():
    return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    def set_password(self, password: str) -> None:
        self.password_hash = ph.hash(password)

    def check_password(self, password: str) -> bool:
        try:
            return ph.verify(self.password_hash, password)
        except VerifyMismatchError:
            return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Category(db.Model):
    __tablename__ = "categories"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=utcnow)
    
    products = db.relationship("Product", back_populates="category", lazy="dynamic")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class Product(db.Model):
    __tablename__ = "products"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    sku = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(500))
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    low_stock_threshold = db.Column(db.Integer, default=10, nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    category = db.relationship("Category", back_populates="products")
    movements = db.relationship("StockMovement", back_populates="product", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def current_stock(self) -> int:
        in_qty = sum(m.quantity for m in self.movements.filter_by(movement_type="IN").all())
        out_qty = sum(m.quantity for m in self.movements.filter_by(movement_type="OUT").all())
        return in_qty - out_qty

    @property
    def stock_status(self) -> str:
        stock = self.current_stock
        if stock <= 0:
            return "out"
        if stock <= self.low_stock_threshold:
            return "low"
        return "ok"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "sku": self.sku,
            "description": self.description,
            "category_id": self.category_id,
            "low_stock_threshold": self.low_stock_threshold,
            "current_stock": self.current_stock,
            "stock_status": self.stock_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class StockMovement(db.Model):
    __tablename__ = "stock_movements"
    __table_args__ = (
        CheckConstraint("movement_type IN ('IN', 'OUT')", name="check_movement_type"),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    movement_type = db.Column(db.String(3), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(500))
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)

    product = db.relationship("Product", back_populates="movements")
    user = db.relationship("User")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "movement_type": self.movement_type,
            "quantity": self.quantity,
            "note": self.note,
            "created_by": self.created_by,
            "created_by_email": self.user.email if self.user else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "product_name": self.product.name if self.product else None
        }