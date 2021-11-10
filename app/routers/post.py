from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional

from sqlalchemy.sql.functions import current_user, mode
from app import oauth2
from sqlalchemy import func
# from sqlalchemy import func
import app.database as db
from .. import models, schemas, utils, oauth2
from ..orm_db import get_db



router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id" : 1},
            {"title": "title of post 2", "content": "content of post 2", "id" : 2}]


def find_post(id: int):
    for p in my_posts:
        if p["id"] == id:
            return p
    else:
        return "Post not fount"

def find_index_post(id: int):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i
    else:
        return -1



@router.get("/")
async def get_posts():
    db.cursor.execute("""SELECT * FROM posts""")
    posts = db.cursor.fetchall()
    # return {"data" : my_posts}
    return posts

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_post(new_post: schemas.PostCreate):
    # print(new_post.rating)
    # print(new_post.dict())
    # post_dict = new_post.dict()
    # post_dict["id"] = len(my_posts) + 1
    # my_posts.append(post_dict)
    db.cursor.execute("""INSERT INTO posts(title, content, published)
                        VALUES(%s, %s, %s) RETURNING *""", 
                        (new_post.title, new_post.content, new_post.published))
    new_post = db.cursor.fetchall()
    db.conn.commit()
    
    return new_post

@router.get("/latest")
def get_latest_posts():
    # if(len(my_posts) - 1 < 0):
    #     return {"data": "Post not found"}
    # post = my_posts[len(my_posts) - 1]
    db.cursor.execute("""SELECT * FROM posts ORDER BY created_at DESC""")
    post = db.cursor.fetchone()
    if post == None:
        # response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=post)

    return post

@router.get("/{id}")
def get_post(id: int):
    db.cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id)))
    post = db.cursor.fetchone()

    # post = find_post(id)
    if post == None:
        # response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=post)
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    db.cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id)))
    deleted_post = db.cursor.fetchone()
    db.conn.commit()

    # index = find_index_post(id)
    if deleted_post == None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="Post does not exist")
    # my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}")
def update_post(id: int, post: schemas.PostCreate):
    db.cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s
    WHERE id = %s RETURNING *""",
    (post.title, post.content, post.published,str(id)))
    updated_post = db.cursor.fetchone()
    db.conn.commit()

    # index = find_index_post(id)
    if updated_post == None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="Post does not exist")
    # post_dict = post.dict()
    # post_dict['id'] = id
    # my_posts[index] = post_dict
    return updated_post


router_sqlalchemy = APIRouter(
    prefix="/sqlalchemy"
)

# @router_sqlalchemy.get("/", response_model=List[schemas.Post])
@router_sqlalchemy.get("/", response_model=List[schemas.PostOut])
def test_posts(db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    # print(results)

    return results

@router_sqlalchemy.get("/user/posts", response_model=List[schemas.Post])
def test_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    posts = db.query(models.Post).filter(models.Post.user_id == current_user.id).all()
    return posts

@router_sqlalchemy.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def send_post_db(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # print(current_user)
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    # post_dict = 

    new_post = models.Post(user_id = current_user.id, **post.dict())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router_sqlalchemy.get("/latest", response_model=schemas.PostOut)
def get_latest_posts(db: Session = Depends(get_db)):
    
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).order_by(models.Post.created_at.desc())
    if post.first() == None:
        # response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=post)
    return post.first()

@router_sqlalchemy.get("/{id}", response_model=schemas.PostOut)
def get_post_db(id: int, db: Session = Depends(get_db)):
    
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if post == None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="Post does not exist")
    return post


@router_sqlalchemy.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_db(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_request = post_query.first()
    # index = find_index_post(id)
    if post_request == None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="Post does not exist")

    if post_request.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
        detail="Not Authorized to perform requested action")
    # my_posts.pop(index)
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router_sqlalchemy.put("/{id}", response_model=schemas.Post)
def update_post_db(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post_request = post_query.first()

    if post_request == None:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="Post does not exist")

    if post_request.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
        detail="Not Authorized to perform requested action")

    post_query.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()
