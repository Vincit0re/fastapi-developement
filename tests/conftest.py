from venv import create
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.main import app
from app.config import settings
from app.database import get_db
from app.models import Base
from app.oauth2 import create_access_token
from app import schemas, models
import pytest


@pytest.fixture
def session():
    SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return TestingSessionLocal()


@pytest.fixture
def client(session):
    def get_test_db():
        try:
            yield session
        finally:
            session.close()

    # override the get_db dependency
    app.dependency_overrides[get_db] = get_test_db
    return TestClient(app)


def create_user(client, email, password):
    response = client.post("/users/", json={"email": email, "password": password})
    created_user = schemas.UserResponse(**response.json())
    assert response.status_code == 200
    assert created_user.email == email
    return created_user


@pytest.fixture
def token(client):
    new_user = create_user(client, email="testing@gmail.com", password="password123")
    return create_access_token(data={"user_id": new_user.id})


@pytest.fixture
def authorize_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
def test_posts(authorize_client, session):
    owner = create_user(
        authorize_client, email="newuser@gmail.com", password="password123"
    )
    posts_data = [
        {
            "title": "Post 1",
            "content": "Content 1",
            "published": True,
            "owner_id": owner.id,
        },
        {
            "title": "Post 2",
            "content": "Content 2",
            "published": False,
            "owner_id": owner.id,
        },
        {
            "title": "Post 3",
            "content": "Content 3",
            "published": True,
            "owner_id": owner.id,
        },
    ]

    def create_post_model(post_dict):
        return models.Post(**post_dict)

    posts = list(map(create_post_model, posts_data))
    session.add_all(posts)
    session.commit()
    return session.query(models.Post).all()
