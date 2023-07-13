from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from apis.v1.route_login import temp_token_for_user
from apis.v1.route_login import get_user_from_temp_token
from db_repo_users import user_change_password, send_passwordchange_email
from db_session import get_db
from webapps.auth_forms import ChangePasswordRequestForm
from webapps.auth_forms import ChangePasswordForm


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)



@router.get("/changepassword/")
def changepassword1(request: Request):
    return templates.TemplateResponse("change_password1.html", {"request": request})


@router.post("/changepassword/")
async def changepassword2(request: Request, db: Session = Depends(get_db)):
    response = RedirectResponse("/logout", status_code=status.HTTP_303_SEE_OTHER)

    form = ChangePasswordRequestForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            temp_token = temp_token_for_user(form.email, db=db)
            #url = f"{request.url.scheme}://{request.url.hostname}:{request.url.port}" # TODO check for port 80
            url = str(request.url)
            await send_passwordchange_email(
                            email=form.email,
                            token=temp_token["temp_token"],
                            url=url)

            response = templates.TemplateResponse(
                                    "change_password_link.html",
                                    {
                                        "request": request,
                                        "ref": temp_token["temp_token"]
                                    }
            )
        except HTTPException:
            return response
            
    return response


@router.get("/changepassword/{temp_token}")
async def changepassword2(request: Request, temp_token, db: Session = Depends(get_db)):
    user = get_user_from_temp_token(token=temp_token, db=db)
    if user is not None:
        return templates.TemplateResponse(
                        "change_password2.html",
                        {
                            "request": request,
                            "ref": temp_token,
                            "email": user.email
                        }
        )
    else:
        return templates.TemplateResponse("change_password1.html", {"request": request})



@router.post("/changepassword/{temp_token}")
async def changepassword2(request: Request, temp_token, db: Session = Depends(get_db)):
    form = ChangePasswordForm(request)
    await form.load_data()
    if await form.is_valid():
        user = get_user_from_temp_token(token=temp_token, db=db)
        if user is not None:
            if user_change_password(email=user.email, password=form.password, db=db) == None:        
                raise HTTPException(
                            status_code=status.HTTP_302_FOUND,
                            headers={'Location': '/login'},
                            detail="Could not validate credentials"
                )

    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
