from typing import List, Optional
from click import get_current_context
from fastapi import FastAPI, HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db
import copy

router = APIRouter(prefix="/vote", tags=["Vote"])


@router.post(
    "/", status_code=status.HTTP_201_CREATED
)
def add_vote(
    vote: schemas.VoteCreate,
    db: Session = Depends(get_db),
    current_user: schemas.UserResponse = Depends(oauth2.get_current_user),
):
    # check if post exists
    post_to_vote = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post_to_vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {vote.post_id} not found!"
        )
    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id
    )
    found_vote = vote_query.first()
    if found_vote:
        if vote.value == 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Already Voted on this Post!"
            )
        elif vote.value == 0:
            vote_query.delete(synchronize_session=False)
            db.commit()
            return {"message": "Successfully Vote deleted!"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid vote value!"
            )
    else:
        if vote.value == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Vote doesn't exist!"
            )
        db_vote = models.Vote(**vote.dict(), user_id=current_user.id)
        db.add(db_vote)
        db.commit()
        db.refresh(db_vote)
        return {"message": "Successfully Vote added!"}
