from fastapi import FastAPI,Depends,Header
from sqlalchemy.orm import Session
from database import engine,sessionLocal
from model import DevLogs as DevLogsSchema
import db_models

db_models.Base.metadata.create_all(bind=engine)

# add cors middleware
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)   

@app.get("/")
def read_root():
    return {"message":"Welcome to my first project"}

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

#get all logs
@app.get("/logs")
def get_logs(db:Session = Depends(get_db)):
    logs_from_db = db.query(db_models.DevLogs).all()
    return logs_from_db

#get a log by id
@app.get("/logs/{id}")
def get_logs_by_id(id:int,db:Session = Depends(get_db)):
    log_product = db.query(db_models.DevLogs).filter(db_models.DevLogs.id == id).first()
    return log_product

#create a log if only isAdmin = true in headers
@app.post("/logs")
def create_log(log: DevLogsSchema,db:Session = Depends(get_db),isAdmin:bool = Header(default=False)):
    if not isAdmin:
        return {"message":"Unauthorized"}
    log_from_db = db_models.DevLogs(**log.dict())
    db.add(log_from_db)
    db.commit()
    db.refresh(log_from_db)
    return log_from_db

#update a log if only isAdmin = true in headers
@app.put("/logs/{id}")
def update_log(id:int,log: DevLogsSchema,db:Session = Depends(get_db),isAdmin:bool = Header(default=False)):
    if not isAdmin:
        return {"message":"Unauthorized"}
    log_from_db = db.query(db_models.DevLogs).filter(db_models.DevLogs.id == id).first()
    if log_from_db is None:
        return {"message":"Log not found"}
    log_from_db.title = log.title
    log_from_db.description = log.description
    log_from_db.links = log.links
    log_from_db.images = log.images
    log_from_db.takeaway = log.takeaway
    db.commit()
    db.refresh(log_from_db)
    return log_from_db

#delete a log if only isAdmin = true in headers
@app.delete("/logs/{id}")
def delete_log(id:int,db:Session = Depends(get_db),isAdmin:bool = Header(default=False)):
    if not isAdmin:
        return {"message":"Unauthorized"}
    log_from_db = db.query(db_models.DevLogs).filter(db_models.DevLogs.id == id).first()
    if log_from_db is None:
        return {"message":"Log not found"}
    db.delete(log_from_db)
    db.commit()
    return {"message":"Log deleted successfully"}


