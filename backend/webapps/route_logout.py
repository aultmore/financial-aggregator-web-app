from fastapi import APIRouter, Depends, HTTPException, Request, status
#from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/logout")
def logout(request: Request):
    # response = RedirectResponse(
    #             "/login",
    #             status_code=status.HTTP_302_FOUND
    # )
    response = templates.TemplateResponse("logout.html", {"request": request})
    response.set_cookie(key="access_token", value=None, httponly=True)
    return response
