from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from datetime import datetime

from db_model import User
from db_session import get_db
from apis.v1.route_login import get_current_user_from_token
from schema_transactions import TransactionRecord
from db_repo_transactions import check_transaction_for_user
from db_repo_users import get_user
from webapps.users_forms import TransactionConfirmForm


templates = Jinja2Templates(directory="templates")
router = APIRouter()


@router.post("/txid")
async def check_txid(request: Request,
                        current_user: User = Depends(get_current_user_from_token),
                        db: Session = Depends(get_db)):
    form = TransactionConfirmForm(request)
    await form.load_data()
    if await form.is_valid():
        check_transaction_for_user(
            user=current_user,
            txid=form.txid,
            db=db)
        
    return templates.TemplateResponse("general_pages/check_txid.html", form.__dict__)


# def test_pay(user_email: str, amount: int, db: Session = Depends(get_db)):
#     user = get_user(email=user_email, db=db)
#     if(user is not None):
#         tr = TransactionRecord(
#             hash_string = str(datetime.now()),
#             result = "RECEIVED",    # TODO Check
#             is_confirmed = True,
#             block_string = str(datetime.now()),
#             date = datetime.now(),
#             amount = amount * 1000000,
#             operation = "RECV",     # TODO operations names
#             from_address = user.email,
#             to_address = "system", # TODO system address
#             user_email = user.email,
#             user_id = user.id
#         )
#         record = create_new_transaction(record=tr, user_id=tr.user_id, db=db)
#         process_income(record=record, db=db)
#         return 0
#     return 1


# @router.get("/pay/52/{user_email}")
# def test_pay52(user_email: str, db: Session = Depends(get_db)):
#     test_pay(user_email=user_email, amount=52, db=db)
#     return RedirectResponse("/dashboard", status_code=status.HTTP_302_FOUND)


# @router.get("/pay/100/{user_email}")
# def test_pay100(user_email: str, db: Session = Depends(get_db)):
#     test_pay(user_email=user_email, amount=100, db=db)
#     return RedirectResponse("/dashboard", status_code=status.HTTP_302_FOUND)
