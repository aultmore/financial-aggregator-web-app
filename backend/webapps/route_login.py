from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from apis.v1.route_login import login_for_access_token
#from apis.v1.route_login import temp_token_for_user
#from apis.v1.route_login import get_user_from_temp_token
from db_session import get_db
from webapps.auth_forms import LoginForm


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/login/")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login/")
async def login(request: Request, db: Session = Depends(get_db)):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            #form.__dict__.update(msg="Login Successful :)")
            #response = templates.TemplateResponse("login.html", form.__dict__)
            response = RedirectResponse("/dashboard/", status_code=status.HTTP_303_SEE_OTHER)
            login_for_access_token(response=response, form_data=form, db=db)
            return response
            
        except HTTPException as e:
            if e.status_code == status.HTTP_302_FOUND:
                raise e     # raise exception for "not validated email"

            form.__dict__.update(msg="")
            form.__dict__.get("errors").append(e.detail)
            return templates.TemplateResponse("login.html", form.__dict__)
    return templates.TemplateResponse("login.html", form.__dict__)

