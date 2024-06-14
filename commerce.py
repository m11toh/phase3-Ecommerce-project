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

# CRUD functions
def create_user(username, email, password):
    new_user = User(username=username, email=email, password=password)
    session.add(new_user)
    session.commit()

def create_product(name, price):
    new_product = Product(name=name, price=price)
    session.add(new_product)
    session.commit()

def create_order(user_id, product_id, quantity):
    new_order = Order(user_id=user_id)
    session.add(new_order)
    session.flush()  # This will populate new_order.id
    new_order_product = OrderProduct(order_id=new_order.id, product_id=product_id, quantity=quantity)
    session.add(new_order_product)
    session.commit()

def read_users():
    return session.query(User).all()

def read_products():
    return session.query(Product).all()

def read_orders():
    return session.query(Order).all()

def update_user(user_id, new_username=None, new_email=None, new_password=None):
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        if new_username:
            user.username = new_username
        if new_email:
            user.email = new_email
        if new_password:
            user.password = new_password
        session.commit()
    else:
        print("User not found")

def delete_user(user_id):
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        session.delete(user)
        session.commit()
    else:
        print("User not found")

# Command line interface
def main():
    while True:
        print("\nChoose an action:")
        print("1. Create User")
        print("2. Create Product")
        print("3. Create Order")
        print("4. View Users")
        print("5. View Products")
        print("6. View Orders")
        print("7. Update User")
        print("8. Delete User")
        print("9. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            username = input("Enter username: ")
            email = input("Enter email: ")
            password = input("Enter password: ")
            create_user(username, email, password)
        elif choice == '2':
            name = input("Enter product name: ")
            price = float(input("Enter product price: "))
            create_product(name, price)
        elif choice == '3':
            user_id = int(input("Enter user ID: "))
            product_id = int(input("Enter product ID: "))
            quantity = int(input("Enter quantity: "))
            create_order(user_id, product_id, quantity)
        elif choice == '4':
            users = read_users()
            for user in users:
                print(user.id, user.username, user.email)
        elif choice == '5':
            products = read_products()
            for product in products:
                print(product.id, product.name, product.price)
        elif choice == '6':
            orders = read_orders()
            for order in orders:
                print(order.id, order.user_id, order.products)
        elif choice == '7':
            user_id = int(input("Enter user ID to update: "))
            new_username = input("Enter new username (press enter to skip): ")
            new_email = input("Enter new email (press enter to skip): ")
            new_password = input("Enter new password (press enter to skip): ")
            update_user(user_id, new_username, new_email, new_password)
        elif choice == '8':
            user_id = int(input("Enter user ID to delete: "))
            delete_user(user_id)
        elif choice == '9':
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
