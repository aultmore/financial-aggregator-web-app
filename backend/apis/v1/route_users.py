from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import json

from schema_users import UserCreate, ShowUser
from db_session import get_db
from db_repo_users import create_new_user, list_user_network, user_network_levels, get_user
from db_repo_users import get_user_stats
from apis.v1.route_login import get_current_user_from_token
from db_model import User

router = APIRouter()


# @router.post("/create", response_model = ShowUser)
# async def create_user(user: UserCreate, db: Session = Depends(get_db)):
#     user = await create_new_user(user=user, db=db)
#     return user


@router.get("/network", response_model = ShowUser)
def user_network(ref_user_email: str,
              #current_user: User = Depends(get_current_user_from_token),
              db: Session = Depends(get_db)):
    # if current_user.email != ref_user_email:
    #     raise HTTPException(
    #                 status_code=status.HTTP_302_FOUND,
    #                 headers={'Location': '/login'},
    #                 detail="Not authenticated")

    users = list_user_network(ref_user_email=ref_user_email, db=db)
    return users

def user_levels(user_email: str, db: Session):
    levels = user_network_levels(user_email=user_email, db=db)
    return levels

@router.get("/levels")
def levels(user_email: str,
           current_user: User = Depends(get_current_user_from_token),
           db: Session = Depends(get_db)):
    if current_user.email != ref_user_email:
        raise HTTPException(
                    status_code=status.HTTP_302_FOUND,
                    headers={'Location': '/login'},
                    detail="Not authenticated")
    return user_levels(user_email=user_email, db=db)



#
# Returns user level to refresh the dashboard page (level 0 -> 1)
#
@router.get("/userlevel")
def levels(current_user: User = Depends(get_current_user_from_token),
           db: Session = Depends(get_db)):
    user = get_user(email=current_user.email, db=db)
    return { "level": user.level }
