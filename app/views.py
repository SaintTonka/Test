from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app import services, auth
from app.database import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/process_payment")
async def process_payment(data: dict, db: Session = Depends(get_db)):
    services.process_payment(data, db)
    return JSONResponse(content={"status": "success"})

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    return {"access_token": "some_token", "token_type": "bearer"}