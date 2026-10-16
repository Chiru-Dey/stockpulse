import random
from datetime import datetime, timedelta, timezone
from app import create_app
from app.extensions import db
from app.models import User, Category, Product, StockMovement

app = create_app()

def seed():
    with app.app_context():
        # 1. Wipe existing data for a clean slate
        print("Clearing existing data...")
        StockMovement.query.delete()
        Product.query.delete()
        Category.query.delete()
        User.query.delete()
        db.session.commit()

        # 2. Create Users
        print("Creating users...")
        admin = User(email="admin@stockpulse.com", is_admin=True)
        admin.set_password("password123")
        
        staff = User(email="staff@stockpulse.com", is_admin=False)
        staff.set_password("password123")
        
        db.session.add_all([admin, staff])
        db.session.commit()

        # 3. Create Categories
        print("Creating categories...")
        cat_electronics = Category(name="Electronics", description="Gadgets and devices")
        cat_furniture = Category(name="Furniture", description="Office and home furniture")
        cat_stationery = Category(name="Stationery", description="Pens, paper, and supplies")
        
        db.session.add_all([cat_electronics, cat_furniture, cat_stationery])
        db.session.commit()

        # 4. Create Products
        print("Creating products...")
        products = [
            Product(name="Gaming Laptop", sku="EL-LAP-01", category_id=cat_electronics.id, low_stock_threshold=5),
            Product(name="Wireless Mouse", sku="EL-MOU-02", category_id=cat_electronics.id, low_stock_threshold=10),
            Product(name="Ergonomic Chair", sku="FR-CHR-01", category_id=cat_furniture.id, low_stock_threshold=3),
            Product(name="Standing Desk", sku="FR-DSK-02", category_id=cat_furniture.id, low_stock_threshold=2),
            Product(name="A4 Notebook", sku="ST-NBK-01", category_id=cat_stationery.id, low_stock_threshold=50),
            Product(name="Ballpoint Pen (Box)", sku="ST-PEN-02", category_id=cat_stationery.id, low_stock_threshold=20),
        ]
        db.session.add_all(products)
        db.session.commit()

        # 5. Create Stock Movements
        print("Creating stock movements...")
        
        def add_movement(product, type, qty, user, days_ago=0):
            m = StockMovement(
                product_id=product.id,
                movement_type=type,
                quantity=qty,
                note=f"Seed data: {type} movement",
                created_by=user.id
            )
            # Manually adjust created_at for visual variety in the UI
            m.created_at = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=random.randint(1, 10))
            db.session.add(m)

        # Laptops: IN 20, OUT 15 -> Stock 5 (Status: Low)
        add_movement(products[0], "IN", 20, admin, days_ago=5)
        add_movement(products[0], "OUT", 15, staff, days_ago=1)

        # Mice: IN 50, OUT 10 -> Stock 40 (Status: OK)
        add_movement(products[1], "IN", 50, admin, days_ago=10)
        add_movement(products[1], "OUT", 10, staff, days_ago=2)

        # Chairs: IN 10, OUT 10 -> Stock 0 (Status: Out)
        add_movement(products[2], "IN", 10, admin, days_ago=15)
        add_movement(products[2], "OUT", 10, staff, days_ago=3)

        # Desks: IN 5 -> Stock 5 (Status: OK)
        add_movement(products[3], "IN", 5, admin, days_ago=2)

        # Notebooks: IN 100, OUT 60 -> Stock 40 (Status: Low)
        add_movement(products[4], "IN", 100, admin, days_ago=20)
        add_movement(products[4], "OUT", 60, staff, days_ago=1)

        # Pens: IN 20, OUT 5 -> Stock 15 (Status: Low)
        add_movement(products[5], "IN", 20, admin, days_ago=8)
        add_movement(products[5], "OUT", 5, staff, days_ago=4)

        db.session.commit()
        
        print("\n✅ Seed data created successfully!")
        print("Admin Login: admin@stockpulse.com / password123")
        print("Staff Login: staff@stockpulse.com / password123")

if __name__ == "__main__":
    seed()