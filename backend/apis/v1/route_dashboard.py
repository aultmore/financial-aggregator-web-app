from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from fastapi.templating import Jinja2Templates

from db_session import get_db
from apis.v1.route_login import get_current_user_from_token
from db_model import User

#from schema_tokens import Token    # for users subtree (invites)


templates = Jinja2Templates(directory = "templates")

router = APIRouter()

@router.get("/", response_model=List)
async def user_dashboard(request: Request, current_user: User = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    return templates.TemplateResponse("general_pages/dashboard.html", { "request": request, "current_user": current_user.email })
