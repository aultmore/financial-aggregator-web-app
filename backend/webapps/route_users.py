from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from jose import JWTError, jwt
from pydantic import ValidationError

from db_session import get_db
from db_repo_users import create_new_user, get_user, send_confirmation_email
from schema_users import UserCreate
from webapps.users_forms import UserCreateForm
from db_model import User
from core.config import settings


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/register")
def register(request: Request):
    return templates.TemplateResponse("ask_for_ref.html", {"request": request})


@router.get("/register/{ref}")
def register(request: Request, ref: str = None):
    if ref == None:
        response = templates.TemplateResponse("ask_for_ref.html", {"request": request})
    else:
        response = templates.TemplateResponse(
                        "user_register.html",
                        {
                            "request": request,
                            "ref": ref,
                            "checkPassword": settings.DEBUG_CHECK_PASSWORD
                        })
    
    response.set_cookie(key="access_token", value=None, httponly=True)
    return response


@router.post("/register/{ref}")
async def register(request: Request, ref: str, db: Session = Depends(get_db)):
    form = UserCreateForm(request)
    await form.load_data()
    if await form.is_valid():
        ref_user_id = None
        user_level = 0
        is_superuser = False
        is_confirmed = False

        if ref == settings.SECRET_KEY:
            user_level = settings.SUPERUSER_LEVEL
            is_superuser = True
            is_confirmed = True
        else:
            try:
                payload = jwt.decode(ref, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                #print("reference user.email: ", payload.get("sub"))
                ref_user_id = payload.get("user_id")
                #print("reference user.id:    ", ref_user_id)

            except JWTError:
                form.__dict__.get("errors").append("Регистрация возможна только по приглашению.")
                return templates.TemplateResponse("user_register.html", form.__dict__)

        try:
            user = UserCreate(
                email = form.email,
                password = form.password,
                tlg_username = form.tlg_username,
                is_adult = True if form.isAdult == "1" else False,
                is_agreed = True if form.isAgreed == "1" else False,
                is_confirmed = is_confirmed,
                ref_user = ref_user_id,
                is_superuser = is_superuser,
                level = user_level
            )
        except ValidationError as e:
            form.__dict__.get("errors").append("Проверьте правильность email адреса.")
            return templates.TemplateResponse("user_register.html", form.__dict__)

        try:
            user = await create_new_user(user=user, db=db)

            if user.is_superuser == False:
                if settings.DBG_SKIP_EMAIL_CONFIRM is not None:
                    user.is_confirmed = True
                    db.commit()
                else:
                    #url_scheme = request.url.scheme,
                    #url_hostname = str(request.url.hostname),
                    #url_port = str(request.url.port)
                    #url = f"{url_scheme}://{url_hostname}:{url_port}"
                    await send_confirmation_email(user=user, url="http://evatoken.net")

            if user.is_confirmed == True:
                return RedirectResponse(
                        "/?msg=Successfully-Registered",
                        status_code=status.HTTP_302_FOUND
                )
            else:
                return RedirectResponse(
                        f"/not_confirmed/{user.email}",
                        status_code=status.HTTP_302_FOUND
                )
        except IntegrityError as e:
            print(e)
            form.__dict__.get("errors").append("Пользователь с таким e-mail уже зарегистрирован.")
            return templates.TemplateResponse("user_register.html", form.__dict__)

    return templates.TemplateResponse("user_register.html", form.__dict__)


@router.get("/confirm_email/{token}")
def validate_user_email(token: str, db: Session = Depends(get_db)):
    exception = HTTPException(
                    status_code=status.HTTP_302_FOUND,
                    headers={'Location': '/login'},
                    detail="Could not validate credentials"
    )
    if token is None:
        raise exception
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("user_id")
        user = get_user(id=user_id, db=db)
        if user is None:
            raise exception
        user.is_confirmed = True
        db.commit()
        return RedirectResponse(
                    "/login",
                    status_code=status.HTTP_302_FOUND
        )
    except JWTError:
        raise exception


@router.get("/not_confirmed/{user_email}")
def email_not_confirmed(user_email: str, request: Request):
    return templates.TemplateResponse(
                "email_not_confirmed.html",
                {
                    "request": request,
                    "user_email": user_email
                }
    )


@router.get("/send_confirm_email/{user_email}")
async def confirm_email(user_email: str, db: Session = Depends(get_db)):
    user = get_user(email=user_email, db=db)
    if user is not None:
        await send_confirmation_email(user)

    raise HTTPException(
                status_code=status.HTTP_302_FOUND,
                headers={'Location': '/login'},
                detail="Please, login")