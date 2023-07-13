from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from db_session import get_db
from apis.v1.route_login import get_current_user_from_token
from db_model import User

from webapps import route_login
from webapps import route_logout
from webapps import route_users
from webapps import dashboard
from webapps import route_changepass
from webapps import route_withdraw
from webapps import help


api_router = APIRouter()
api_router.include_router(route_login.router, prefix="", tags=["webapps-auth"])
api_router.include_router(route_logout.router, prefix="", tags=["webapps-auth"])
api_router.include_router(route_changepass.router, prefix="", tags=["webapps-auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["webapp-dashboard"])
api_router.include_router(route_users.router, prefix="", tags=["webapp-users"])
api_router.include_router(route_withdraw.router, prefix="", tags=["webapp-users"])
api_router.include_router(help.router, prefix="", tags=["webapps-users"])


@api_router.get("/")
async def webapp_home(request: Request, current_user: User = Depends(get_current_user_from_token), db: Session = Depends(get_db)):
    return RedirectResponse(
                        "/dashboard",
                        status_code=status.HTTP_302_FOUND
            )
