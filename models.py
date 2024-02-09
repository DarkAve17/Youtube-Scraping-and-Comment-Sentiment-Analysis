from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from database import Base

class YoutubeData(Base):  
    __tablename__ = "Comments Data"  
    
    ID = Column(Integer, primary_key=True, unique= True)
    Author = Column(String, index=True) 
    Comment = Column(String, index=True) 
    