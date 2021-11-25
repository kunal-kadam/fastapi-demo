from typing import List

from sqlalchemy import schema
from app import schemas

import pytest

def validate(post):
    return schemas.PostOut(**post)

def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/sqlalchemy/")
    print(res.json())
    # posts = schemas.PostOut(res.json())
    posts_map = map(validate,res.json())
    # print(list(posts_map))
    posts_list = list(posts_map)

    assert len(res.json()) == len(test_posts)
    assert res.status_code == 200
    # assert posts_list[0].Post.id == test_posts[0].id

def test_unauthorized_user_get_all_posts(client, test_posts):
    res = client.get("/sqlalchemy/user/posts")
    assert res.status_code == 401

# def test_unauthorized_user_get_one_posts(client, test_posts):
#     res = client.get(f"/sqlalchemy/{test_posts[0].id}")
#     assert res.status_code == 401

def test_get_one_post_not_exist(authorized_client, test_posts):
    res = authorized_client.get(f"/sqlalchemy/888")
    assert res.status_code == 404

def test_get_one_post(authorized_client, test_posts):
    res = authorized_client.get(f"/sqlalchemy/{test_posts[0].id}")
    # print(res.json())
    post = schemas.PostOut(**res.json())
    assert post.Post.id == test_posts[0].id
    assert post.Post.content == test_posts[0].content
    assert post.Post.title == test_posts[0].title

@pytest.mark.parametrize("title, content, published", [
    ("awesome new title", "awesom new content", True),
    ("Favouriate pizza", "I love peprone", False),
    ("Taaller skyscaper", "hwty new content", True),
])
def test_create_post(authorized_client, test_user, test_posts, title, content, published):
    res = authorized_client.post("/sqlalchemy/posts", json={"title": title, "content" : content, "published" : published})
    
    created_post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.user_id == test_user['id'] 

def test_create_post_default_published_true(authorized_client, test_user, test_posts):
    res = authorized_client.post("/sqlalchemy/posts", json={"title": "some new title", "content" : "some exciting content"})
    
    created_post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == "some new title"
    assert created_post.content == "some exciting content"
    assert created_post.published == True
    assert created_post.user_id == test_user['id']

def test_unauthorized_user_create_post(client, test_user, test_posts):
    res = client.post("/sqlalchemy/posts", json={"title": "some new title", "content" : "some exciting content"})
    assert res.status_code == 401

def test_unauthorized_user_delete_Post(client, test_user, test_posts):
    res = client.delete(f"/sqlalchemy/{test_posts[0].id}")
    assert res.status_code == 401

def test_delete_post_success(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/sqlalchemy/{test_posts[0].id}")
    assert res.status_code == 204

def test_delete_post_non_exist(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/sqlalchemy/888")
    assert res.status_code == 404

def test_delete_other_user_post(authorized_client, test_user, test_posts):
    res = authorized_client.delete(f"/sqlalchemy/{test_posts[3].id}")
    assert res.status_code == 403

def test_update_post(authorized_client, test_user, test_posts):
    data = {
        "title" : "updated post title",
        "content" : "updated post content",
        "id" : test_posts[0].id
    }
    res = authorized_client.put(f"/sqlalchemy/{test_posts[0].id}", json = data)
    updated_post = schemas.Post(**res.json())
    assert res.status_code == 200
    assert updated_post.title == data['title']
    assert updated_post.content == data['content']


def test_update_other_user_post(authorized_client, test_user, test_posts):
    data = {
        "title" : "updated post title",
        "content" : "updated post content",
        "id" : test_posts[3].id
    }
    res = authorized_client.put(f"/sqlalchemy/{test_posts[3].id}", json = data)
    assert res.status_code == 403


def test_unauthorized_user_update_Post(client, test_user, test_posts):
    data = {
        "title" : "updated post title",
        "content" : "updated post content",
        "id" : test_posts[3].id
    }
    res = client.put(f"/sqlalchemy/{test_posts[0].id}",json = data )
    assert res.status_code == 401

def test_update_post_non_exist(authorized_client, test_user, test_posts):
    data = {
        "title" : "updated post title",
        "content" : "updated post content",
        "id" : test_posts[3].id
    }
    res = authorized_client.put(f"/sqlalchemy/888", json = data)
    assert res.status_code == 404