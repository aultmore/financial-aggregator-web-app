from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from urllib.parse import urlparse

from db_session import get_db
from db_model import User
from apis.v1.route_login import get_current_user_from_token
from apis.v1.route_users import user_levels
from core.config import settings, LEVELS_PRICES, MAXIMUM_LEVEL
from db_repo_users import get_user_stats



templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)



@router.get("/help")
def help_page(request: Request,
            current_user: User = Depends(get_current_user_from_token),
            db: Session = Depends(get_db)):
    
    return templates.TemplateResponse(
                "general_pages/help.html",
                {
                    "request": request
                }
    )
