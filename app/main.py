from fastapi import FastAPI
from app.database import create_db  
from app.views import app

async def lifespan(app: FastAPI):

    create_db() 

    yield  
    
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
