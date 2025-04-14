from sqlalchemy import Column, Integer, String
from app.database import Base

class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
