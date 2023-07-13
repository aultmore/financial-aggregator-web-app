from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from apis.v1.send_trx import send_trx

from db_model import User
from apis.v1.route_login import get_current_user_from_token
from db_repo_users import user_update_balance
from db_repo_transactions import create_transaction_withdraw
from db_session import get_db
from webapps.users_forms import WithdrawRequestForm


templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)




async def withdraw_user_balance(user: User, amount: int, to_address: str, db: Session):
    create_transaction_withdraw(
                user=user,
                amount=amount,
                to_address=to_address,
                db=db
    )
    return 0



@router.get("/withdraw/")
def withdraw_form(request: Request,
                    current_user: User = Depends(get_current_user_from_token),
                    db: Session = Depends(get_db)):
    return templates.TemplateResponse(
                "general_pages/withdraw.html",
                {
                    "request": request,
                    "balance": int(current_user.balance / 1000000)
                }
    )


@router.post("/withdraw/")
async def withdraw(request: Request,
                    current_user: User = Depends(get_current_user_from_token),
                    db: Session = Depends(get_db)):
    form = WithdrawRequestForm(request)
    await form.load_data()
    if await form.is_valid():
        withdraw_user_balance(
            user=current_user,
            amount=form.amount * 1000000,
            to_address=form.to_address,
            db=db)
        send_trx(to_address=form.to_address, amount=int(form.amount))
        user_update_balance(email=current_user.email, amount=100 * 1_000_000, db=db)
        return RedirectResponse("/", status.HTTP_302_FOUND)

    return templates.TemplateResponse("general_pages/withdraw.html", form.__dict__)
