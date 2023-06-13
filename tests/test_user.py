from app import schemas
from .database import client, session
import pytest
from fastapi import status, HTTPException
from app.oauth2 import verify_access_token


def create_user(client, email, password):
    response = client.post("/users/", json={"email": email, "password": password})
    created_user = schemas.UserResponse(**response.json())
    assert response.status_code == 200
    assert created_user.email == email


# root endpoint
def test_root(client, session):
    """Testing the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World!"}


# create user endpoint
# login user endpoint
@pytest.mark.parametrize(
    "email, password",
    [
        ("testing@gmail.com", "password123"),
        ("fightclub@gmail.com", "hollywood"),
        ("terenaam@gmail.com", "bollywood"),
    ],
)
def test_create_user(client, email, password):
    """Testing the create user endpoint"""
    response = client.post(
        "/users/", json={"email": f"{email}", "password": f"{password}"}
    )
    created_user = schemas.UserResponse(**response.json())
    assert response.status_code == 200
    assert created_user.email == email


# login user endpoint
@pytest.mark.parametrize(
    "username, password",
    [
        ("testing@gmail.com", "password123"),
        ("fightclub@gmail.com", "hollywood"),
        ("terenaam@gmail.com", "bollywood"),
    ],
)
def test_login_user(client, username, password):
    """Testing the login user endpoint"""
    create_user(client, username, password)
    response = client.post(
        "/login", data={"username": f"{username}", "password": f"{password}"}
    )
    login_token = schemas.Token(**response.json())
    if verify_access_token(
        login_token.access_token,
        HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not find user for given credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        ),
    ):
        assert response.status_code == 201
        assert login_token.token_type == "bearer"
