from fastapi import FastAPI
from controllers.pollution_controller import router as pollution_router
from config.database_config import engine, Base
from fastapi.middleware.cors import CORSMiddleware
from controllers.websocket_controller import socket_router

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

app.include_router(pollution_router, prefix="/api")
app.include_router(socket_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Phewa Lake Pollution Tracker API"}