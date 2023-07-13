from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import Depends, APIRouter, Response
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi import status, HTTPException
from jose import jwt, JWTError

from db_session import get_db
from core.hashing import Hasher
from schema_tokens import Token, TempToken
from db_repo_users import authenticate_user, get_user, find_user, set_temp_token_for_user
from core.security import create_access_token
from core.config import settings
from apis.utils import OAuth2PasswordBearerWithCookie


router = APIRouter()



@router.post("/token", response_model=Token)
def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = None
    try:
        user = authenticate_user(form_data.email, form_data.password, db)
    except Exception as e:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=e.args[0]
        )

    if not user:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неправильный логин или пароль!"
        )

    if user.is_confirmed == False:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND,
            headers={'Location': f'/not_confirmed/{user.email}'},
            detail="Email is not confirmed"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/temptoken", response_model=TempToken)
def temp_token_for_user(email, db: Session = Depends(get_db)):
    user = find_user(email, db)
    if not user:
        raise HTTPException(
                status_code=status.HTTP_302_FOUND,
                headers={'Location': '/login'},
                detail="Could not validate credentials"
        )

    temp_token_expires = timedelta(minutes=settings.TEMP_TOKEN_EXPIRE_MINUTES)
    temp_token = create_access_token(
        data={"sub": user.email},
        expires_delta=temp_token_expires
    )
    set_temp_token_for_user(email=email, temp_token=temp_token, db=db)
    return {"temp_token": temp_token }


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login/token")

def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_302_FOUND,
        headers={'Location': '/login'},
        detail="Could not validate credentials"
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        #print("username/email extracted is ", username)
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = get_user(email=username, db=db)
    if user is None:
        raise credentials_exception

    return user

#
# Returns User found by temporary token (for password change etc)
#
def get_user_from_temp_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # credentials_exception = HTTPException(
    #     status_code=status.HTTP_302_FOUND,
    #     headers={'Location': '/login'},
    #     detail="Could not validate credentials"
    # )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        #print("username/email extracted is ", username)
        if username is None:
            #raise credentials_exception
            return None
    except JWTError:
        #raise credentials_exception
        return None
    
    user = get_user(email=username, db=db)
    if user is None:
        #raise credentials_exception
        return None

    return user
