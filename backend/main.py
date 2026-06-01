from fastapi import FastAPI,Depends,Header
from sqlalchemy.orm import Session
from database import engine,sessionLocal
from model import DevLogs as DevLogsSchema, DevLogsResponse, UserCreate, UserResponse
from fastapi.security import OAuth2PasswordRequestForm
import auth
from datetime import timedelta
import db_models
from fastapi import HTTPException, status
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

@app.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(db_models.User).filter(db_models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = db_models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(db_models.User).filter(db_models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

#get all logs
@app.get("/logs", response_model=list[DevLogsResponse])
def get_logs(db:Session = Depends(get_db)):
    logs_from_db = db.query(db_models.DevLogs).all()
    return logs_from_db

#get a log by id
@app.get("/logs/{id}", response_model=DevLogsResponse)
def get_logs_by_id(id:int,db:Session = Depends(get_db)):
    log_product = db.query(db_models.DevLogs).filter(db_models.DevLogs.id == id).first()
    return log_product

#create a log if authenticated
@app.post("/logs", response_model=DevLogsResponse)
def create_log(log: DevLogsSchema, db: Session = Depends(get_db), current_user: db_models.User = Depends(auth.get_current_user)):
    log_from_db = db_models.DevLogs(**log.dict())
    db.add(log_from_db)
    db.commit()
    db.refresh(log_from_db)
    return log_from_db

#update a log if authenticated
@app.put("/logs/{id}", response_model=DevLogsResponse)
def update_log(id: int, log: DevLogsSchema, db: Session = Depends(get_db), current_user: db_models.User = Depends(auth.get_current_user)):
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

#delete a log if authenticated
@app.delete("/logs/{id}")
def delete_log(id: int, db: Session = Depends(get_db), current_user: db_models.User = Depends(auth.get_current_user)):
    log_from_db = db.query(db_models.DevLogs).filter(db_models.DevLogs.id == id).first()
    if log_from_db is None:
        return {"message":"Log not found"}
    db.delete(log_from_db)
    db.commit()
    return {"message":"Log deleted successfully"}


