from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

import models
from database import get_db
from schemas import PostCreate, PostResponse, PostUpdate

router = APIRouter()

# Post Methods for FastAPI que responderan a NestJS que al final le Mandará las respuestas al Frontend en Angular.
@router.get("", response_model=list[PostResponse], tags=["Endpoins ~ Posts"])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.models.Post).options(selectinload(models.models.Post.author)))
    posts = result.scalars().all()
    return posts

@router.get("/{id}", response_model=PostResponse, tags=["Endpoins ~ Posts"])
async def get_post(id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.models.Post).options(selectinload(models.models.Post.author)).where(models.models.Post.id == id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED, tags=["Endpoins ~ Posts"])
async def create_post(post: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.models.User).options(selectinload(models.models.Post.author)).where(models.models.User.id == post.user_id))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found.")
    
    new_post = models.models.Post(title=post.title, content=post.content, user_id=post.user_id)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.put("/{id}", response_model=PostResponse, status_code=status.HTTP_200_OK, tags=["Endpoins ~ Posts"])
async def update_post_full(id: int, post_data: PostCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.models.Post).options(selectinload(models.models.Post.author)).where(models.models.Post.id == id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post_data.user_id != post.user_id:
        result = await db.execute(select(models.models.User).options(selectinload(models.models.Post.author)).where(models.models.User.id == post_data.user_id))
        user = result.scalars().first()
        if not user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not Found.")    
                    
    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id

    db.commit()
    db.refresh(post)
    return post


@router.patch("/{id}", response_model=PostResponse, status_code=status.HTTP_200_OK, tags=["Endpoins ~ Posts"])
async def update_post_partial(id: int, post_data: PostUpdate, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.models.Post).where(models.models.Post.id == id))
    post = result.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    update_data = post_data.model_dump(exclude_unset=True) # Se validan los campos a ser Actualizados, devolviendo un Diccionario con los vlores a cambiar.
    for field, value in update_data.items():
        setattr(post, field, value)
    
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Endpoins ~ Posts"])
async def delete_post(id: int, db: Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(models.models.Post).where(models.models.Post.id == id))
    post = result.scalars().first()

    if not post: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    db.delete(post)
    db.commit()

