"""
file: main.py
author: @vincit0re
brief: main file for the project
date: 2023-05-26
"""

from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models
from .database import engine, get_db
from .routers import post, user, auth, vote
from fastapi.middleware.cors import CORSMiddleware

# database setup
# models.Base.metadata.create_all(bind=engine)
# app instance
app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routers
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)


# paths
@app.get("/")
async def root(db: Session = Depends(get_db)):
    return {"message": "Hello World!"}
