from fastapi import APIRouter

from apis.v1 import route_general_pages
from apis.v1 import route_users
from apis.v1 import route_login
from apis.v1 import route_dashboard
from apis.v1 import route_transactions
from apis.v1 import background_proc


api_router = APIRouter()
#api_router.include_router(route_general_pages.general_pages_router, prefix="", tags=["general_pages"])
api_router.include_router(route_users.router, prefix="/users", tags=["users"])
api_router.include_router(route_login.router, prefix="/login", tags=["login"])
#api_router.include_router(route_dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(route_transactions.router, prefix="", tags=["transactions"])
api_router.include_router(background_proc.router, prefix="", tags=["background"])
