from app import schemas
import pytest


def test_get_all_posts(authorize_client, test_posts):
    """Testing the get all posts endpoint"""
    response = authorize_client.get("/posts/")

    def validate(post_dict):
        return schemas.PostOut(**post_dict)

    posts = list(map(validate, response.json()))
    assert response.status_code == 200
    assert len(response.json()) == len(posts)


def test_unauthorized_client_all_posts(client):
    """Testing the get all posts endpoint"""
    response = client.get("/posts/")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_unauthorized_client_one_post(client, test_posts):
    """Testing the get one post endpoint"""
    response = client.get(f"/posts/{test_posts[0].id}")
    assert response.status_code == 200


def test_post_not_exist(client, test_posts):
    """Testing the get one post endpoint when the given id post does not exists"""
    response = client.get(f"/posts/{len(test_posts)+1}")
    assert response.status_code == 404
    assert (
        response.json().get("detail") == f"Post with id {len(test_posts)+1} not found!"
    )


def test_get_one_post(authorize_client, test_posts):
    """Testing get one post with given id endpoint"""
    response = authorize_client.get(f"/posts/{test_posts[0].id}")
    post = schemas.PostOut(**response.json())
    assert response.status_code == 200
    assert post.Post.id == test_posts[0].id


@pytest.mark.parametrize(
    "title, content, published",
    [
        ("New Post", "New Content", True),
        ("One More Post", "One More Content", False),
        ("Yet Another Post", "Yet Another Content", False),
    ],
)
def test_create_post(authorize_client, title, content, published):
    response = authorize_client.post(
        "/posts/", json={"title": title, "content": content, "published": published}
    )
    created_post = schemas.PostResponse(**response.json())
    assert response.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published


def test_create_post_default_published(authorize_client):
    response = authorize_client.post(
        "/posts/", json={"title": "Default Not given Post", "content": "Random Content"}
    )
    created_post = schemas.PostResponse(**response.json())
    assert response.status_code == 201
    assert created_post.title == "Default Not given Post"
    assert created_post.content == "Random Content"
    assert created_post.published == True

def test_unauthorized_delete_post(client, test_posts):
    response = client.delete(f"/posts/{test_posts[0].id}")
    assert response.status_code == 403