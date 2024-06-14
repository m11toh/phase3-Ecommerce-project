import argparse
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Create an engine to connect to the SQLite database
engine = create_engine('sqlite:///e_commerce.db', echo=True)

# Create a base class for declarative class definitions
Base = declarative_base()

# Define models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    orders = relationship('Order', back_populates='user')

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='orders')
    products = relationship('OrderProduct', back_populates='order')

class OrderProduct(Base):
    __tablename__ = 'order_products'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    order = relationship('Order', back_populates='products')
    product = relationship('Product')

# Create tables
Base.metadata.create_all(engine)

# Create a session class to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Create
def create_user(username, email, password):
    new_user = User(username=username, email=email, password=password)
    session.add(new_user)
    session.commit()
    return new_user

# Read
def get_user_by_username(username):
    return session.query(User).filter_by(username=username).first()

# Update
def update_user_password(user, new_password):
    user.password = new_password
    session.commit()

# Delete
def delete_user(user):
    session.delete(user)
    session.commit()

def add_product_to_order(order, product, quantity):
    order_product = OrderProduct(order=order, product=product, quantity=quantity)
    session.add(order_product)
    session.commit()

def create_order(user):
    new_order = Order(user=user)
    session.add(new_order)
    session.commit()
    return new_order

def calculate_order_total(order):
    total = 0
    for op in order.products:
        total += op.product.price * op.quantity
    return total

# CLI functions
def cli_create_user(args):
    user = create_user(args.username, args.email, args.password)
    print(f"User created: {user.username}")

def cli_get_user(args):
    user = get_user_by_username(args.username)
    if user:
        print(f"User found: {user.username}, Email: {user.email}")
    else:
        print("User not found")

def cli_update_user_password(args):
    user = get_user_by_username(args.username)
    if user:
        update_user_password(user, args.password)
        print(f"Password updated for user: {user.username}")
    else:
        print("User not found")

def cli_delete_user(args):
    user = get_user_by_username(args.username)
    if user:
        delete_user(user)
        print(f"User deleted: {user.username}")
    else:
        print("User not found")

def cli_create_product(args):
    product = Product(name=args.name, price=args.price)
    session.add(product)
    session.commit()
    print(f"Product created: {product.name}")

def cli_create_order(args):
    user = get_user_by_username(args.username)
    if user:
        order = create_order(user)
        print(f"Order created for user: {user.username}")
    else:
        print("User not found")

def cli_add_product_to_order(args):
    order = session.query(Order).filter_by(id=args.order_id).first()
    product = session.query(Product).filter_by(id=args.product_id).first()
    if order and product:
        add_product_to_order(order, product, args.quantity)
        print(f"Added {args.quantity} of {product.name} to order {order.id}")
    else:
        print("Order or Product not found")

def cli_calculate_order_total(args):
    order = session.query(Order).filter_by(id=args.order_id).first()
    if order:
        total = calculate_order_total(order)
        print(f"Total for order {order.id}: {total}")
    else:
        print("Order not found")

# Main CLI interface
def main():
    parser = argparse.ArgumentParser(description="E-Commerce CLI")

    subparsers = parser.add_subparsers()

    # Create user command
    parser_create_user = subparsers.add_parser('create_user')
    parser_create_user.add_argument('username')
    parser_create_user.add_argument('email')
    parser_create_user.add_argument('password')
    parser_create_user.set_defaults(func=cli_create_user)

    # Get user command
    parser_get_user = subparsers.add_parser('get_user')
    parser_get_user.add_argument('username')
    parser_get_user.set_defaults(func=cli_get_user)

    # Update user password command
    parser_update_user_password = subparsers.add_parser('update_user_password')
    parser_update_user_password.add_argument('username')
    parser_update_user_password.add_argument('password')
    parser_update_user_password.set_defaults(func=cli_update_user_password)

    # Delete user command
    parser_delete_user = subparsers.add_parser('delete_user')
    parser_delete_user.add_argument('username')
    parser_delete_user.set_defaults(func=cli_delete_user)

    # Create product command
    parser_create_product = subparsers.add_parser('create_product')
    parser_create_product.add_argument('name')
    parser_create_product.add_argument('price', type=float)
    parser_create_product.set_defaults(func=cli_create_product)

    # Create order command
    parser_create_order = subparsers.add_parser('create_order')
    parser_create_order.add_argument('username')
    parser_create_order.set_defaults(func=cli_create_order)

    # Add product to order command
    parser_add_product_to_order = subparsers.add_parser('add_product_to_order')
    parser_add_product_to_order.add_argument('order_id', type=int)
    parser_add_product_to_order.add_argument('product_id', type=int)
    parser_add_product_to_order.add_argument('quantity', type=int)
    parser_add_product_to_order.set_defaults(func=cli_add_product_to_order)

    # Calculate order total command
    parser_calculate_order_total = subparsers.add_parser('calculate_order_total')
    parser_calculate_order_total.add_argument('order_id', type=int)
    parser_calculate_order_total.set_defaults(func=cli_calculate_order_total)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
