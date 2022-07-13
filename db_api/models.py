from datetime import datetime

from sqlalchemy import Column, SmallInteger, BigInteger, VARCHAR, ForeignKey, DECIMAL, TIMESTAMP
from sqlalchemy.orm import declarative_base

TGBase = declarative_base()


class Category(TGBase):
    __tablename__: str = 'categories'
    id = Column(SmallInteger, primary_key=True)
    name = Column(VARCHAR(20), nullable=False)
    parent_id = Column(SmallInteger, ForeignKey('categories.id', ondelete='CASCADE'))

    def __repr__(self):
        return f'Категория:{self.id}-{self.name}'
# CREATE TABLE categories(id SERIAL PRIMARY KEY, name VARCHAR(20) UNIQUE NOT NULL);


class Product(TGBase):
    __tablename__: str = 'products'
    id = Column(SmallInteger, primary_key=True)
    name = Column(VARCHAR(50), nullable=False)
    description = Column(VARCHAR(140))
    price = Column(DECIMAL(8, 2), nullable=False)
    category_id = Column(SmallInteger, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False)
    # CREATE TABLE products(id SERIAL PRIMARY KEY, key VARCHAR(20) UNIQUE NOT NULL, full_name VARCHAR(60) NOT NULL, category_id INTEGER NOT NULL REFERENCES categories(id), page INTEGER NOT NULL, on_page SMALLINT NOT NULL);


class Users(TGBase):
    __tablename__: str = 'users'
    id = Column(BigInteger, primary_key=True)
    username = Column(VARCHAR(50), nullable=False)
    first_name = Column(VARCHAR(50))
    last_name = Column(VARCHAR(50))
    referrer = Column(BigInteger, ForeignKey('users.id', ondelete='SET NULL'))
    ref_score = Column(DECIMAL(8, 2))
    time_creation = Column(TIMESTAMP, default=datetime.now())

    def __repr__(self):
        return f'id:{self.id}\nname:{self.username}\nreferrer{self.referrer}'

# CREATE TABLE users(id BIGINT UNIQUE, username VARCHAR(50) NOT NULL, first_name VARCHAR(50), last_name VARCHAR(50), referrer BIGINT REFERENCES users(id), ref_score DECIMAL(8,2), time_creation TIMESTAMP DEFAULT now());


# class Statuses(TGBase):
#     __tablename__: str = 'statuses'
#     id = Column(SmallInteger, primary_key=True)
#     status = Column(VARCHAR(20))


class Orders(TGBase):
    __tablename__: str = 'orders'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'))
    # status_id = Column(SmallInteger, ForeignKey('statuses.id'))
    status = Column(VARCHAR(50))
    amount = Column(DECIMAL(8, 2))
    time_creation = Column(TIMESTAMP, default=datetime.now())
# CREATE TABLE orders(id BIGSERIAL PRIMARY KEY, user_id BIGINT REFERENCES users(id) ON DELETE CASCADE, status VARCHAR(50), amount DECIMAL(8,2), time_creation TIMESTAMP DEFAULT now());


class Basket(TGBase):
    __tablename__: str = 'basket'
    id = Column(BigInteger, primary_key=True)
    order_id = Column(BigInteger, ForeignKey('orders.id', ondelete='CASCADE'))
    product_id = Column(SmallInteger, ForeignKey('products.id', ondelete='CASCADE'))
# CREATE TABLE basket(id BIGSERIAL PRIMARY KEY, order_id BIGINT REFERENCES orders(id) ON DELETE CASCADE, product_id SMALLINT REFERENCES products(id) ON DELETE CASCADE);

