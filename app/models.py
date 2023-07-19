from sqlalchemy import Column, Uuid, String, Text, Float, Integer, Time
from .database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Uuid, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(Time, nullable=False)
    updated_at = Column(Time, nullable=False)
