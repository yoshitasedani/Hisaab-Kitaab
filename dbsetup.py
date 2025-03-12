from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy import inspect
from sqlalchemy import text
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


DATABASE_URL = "sqlite:///accounting_software.db"
engine = create_engine(DATABASE_URL, echo=True)



# Run this after creating your database session



Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    item_id = Column(String, primary_key=True)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    rent = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    availability = Column(Boolean, default=True)
    issued_quantity = Column(Integer, default=0)

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False, unique=True)

class Rental(Base):
    __tablename__ = "rentals"
    rental_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    item_id = Column(String, nullable=False)
    date_of_booking = Column(Date, nullable=False)
    date_of_issuing = Column(Date)  
    due_date = Column(Date)  # Corrected to Date type
    date_of_returning = Column(Date)  # Corrected to Date type
    quantity_issued = Column(Integer, nullable=False)
    quantity_returned = Column(Integer, default=0)
    rent = Column(Float, nullable=False)
    advance = Column(Float, default=0)
    total_rent = Column(Float, nullable=False)
    balance = Column(Float, nullable=False)
    number_of_days = Column(Integer, nullable=False)  

Base.metadata.create_all(engine)

Session = scoped_session(sessionmaker(bind=engine))
session = Session()

print("Database and tables created successfully.")

inspector = inspect(engine)
columns = inspector.get_columns("rentals")

for column in columns:
    print(column["name"])


from sqlalchemy import text
from dbsetup import engine

with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM items WHERE item_id = 444"))
    item = result.fetchone()  # Fetch the first row

    if item:
        print("Item Found:", item)
    else:
        print("Item not found")


