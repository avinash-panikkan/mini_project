from database import Base
from sqlalchemy import Column,Integer,String,ForeignKey,Boolean,Date
from sqlalchemy.orm import relationship


class user(Base):
    __tablename__ = "users"

    id = Column(Integer,primary_key = True,index = True,autoincrement=True)
    name=Column(String) 
    email=Column(String) 
    password=Column(String)
    points = Column(Integer,default=0)
    money = Column(Integer,default=0)
    uid = Column(String)
    role = Column(String,default="user")
    
    product = relationship("Product", back_populates="owner")

    
class Product(Base):
    __tablename__ = "product"

    id = Column(Integer, index=True, primary_key=True)
    pid = Column(String, nullable=True)
    purchased = Column(Boolean, default=False)
    disposed = Column(Boolean, default=False)
    date = Column(String, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    
    owner = relationship("user", back_populates="product")
 
 
class Value(Base):
    __tablename__ = "values"

    id = Column(Integer, index=True, primary_key=True)
    value4m = Column(Integer)
    
    
# class purchase(Base):  
#     __tablename__ = "purchase info"

#     id = Column(Integer,index = True,primary_key = True)
#     pname=Column(String) 
#     pid = Column(String, nullable = True,primary_key = True)
#     puechaserd = Column(Boolean,default=False)
#     uid = Column(String, nullable = True)
#     uname = Column(String)
       
    
    
class garbage(Base):  
    __tablename__ = "garbage"

    id = Column(Integer,index = True,primary_key = True)
    gid = Column(String, nullable = True)
    used= Column(Boolean, default=False) 
    
    
class Plots(Base):
    __tablename__ = "plots"
    
    id = Column(Integer,index = True,primary_key = True)
    name = Column(String)
    points = Column(Integer)
    image = Column(String) 
     