from fastapi import FastAPI, HTTPException, Depends,UploadFile, File, status
from pydantic import BaseModel
from typing import List, Annotated
from models import YoutubeData
from models import Base
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import models
import io
import os
import pandas as pd

app=FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
    db= SessionLocal()
    try: 
        yield db
    finally:
        db.close()
db_dependency = Annotated[Session, Depends(get_db)]
    
#filepathtobe= ("C:\Users\mridu\Documents\GitHub Repos\Youtube Scraping and Sentiment analysis\Youtube_comments.csv")

#to run the models to post all that data into a Table in the DBS
generated_file_name = "Youtube_comments.csv"  # Assuming this is the generated file name


@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):#file: filepathtobe):
    try:
        
        filepathtobe = ('C:\\Users\\mridu\\Documents\\GitHub Repos\\Youtube Scraping and Sentiment analysis\\Youtube_comments.CSV')
        #df = pd.read_csv(file.file)
        df=pd.read_csv(filepathtobe)
        
        data = df.to_dict(orient='records')
        
        with engine.connect() as conn:
            conn.execute(YoutubeData.__table__.insert(),data)
            conn.commit()
            
        return {"Thankyou": "Data uploaded Successfully"}
    except Exception as e:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    

@app.get("/Comment/{ID}")
async def comment_by_id(ID:int, db:db_dependency):
    result = db.query(models.YoutubeData).filter(models.YoutubeData.ID == ID).first()
    if not result:
        raise HTTPException(status_code=404, detail='Data not found')
    return result
        
    
#from YouScrates2 import get_video_link

#@app.get("/get_video_link/{url}")
#async def get_link(url:str):
#    video_link = get_video_link(f'{url}')
#    return {"video_link": video_link}
    