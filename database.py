from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from config import POSTGRES_CONFIG


URL_DATABASE = f"postgresql://{POSTGRES_CONFIG['username']}:{POSTGRES_CONFIG['password']}@{POSTGRES_CONFIG['host']}:{POSTGRES_CONFIG['port']}/{POSTGRES_CONFIG['database']}"

engine= create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush = False, bind=engine)

Base = declarative_base()