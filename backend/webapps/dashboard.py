from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from urllib.parse import urlparse

from db_session import get_db
from db_model import User
from apis.v1.route_login import get_current_user_from_token
from apis.v1.route_users import user_levels
from core.config import settings, LEVELS_PRICES, MAXIMUM_LEVEL
from db_repo_users import get_user_stats, get_boss_user



templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)



@router.get("/")
async def dashboard(request: Request,
                    current_user: User = Depends(get_current_user_from_token),
                    db: Session = Depends(get_db)):
    wanted_level = 0
    wanted_level_price = LEVELS_PRICES[MAXIMUM_LEVEL+1]
    if current_user.level < MAXIMUM_LEVEL:
        wanted_level = current_user.level + 1
        wanted_level_price = LEVELS_PRICES[wanted_level]

    boss_user = get_boss_user(user_id=current_user.id, wanted_level=5, db=db)
    tadr = settings.TRON_ADDRESS
    if boss_user.tron_address is not None:
        tadr = boss_user.tron_address
    print("** boss_user=", tadr)

    #url = f"{request.url.scheme}://{request.url.hostname}:{request.url.port}" # TODO check for port 80
    o = urlparse(str(request.url))
    url = o.scheme + "://" + o.netloc

    user_stat = get_user_stats(user=current_user, db=db)

    # levels_map = user_levels(user_email=current_user.email, db=db)
    # l0_num = levels_map['0'] if '0' in levels_map else 0
    # l1_num = levels_map['1'] if '1' in levels_map else 0
    # l2_num = levels_map['2'] if '2' in levels_map else 0
    # l3_num = levels_map['3'] if '3' in levels_map else 0
    # l4_num = levels_map['4'] if '4' in levels_map else 0

    su1_l4p = 0
    su1_l3p = 0
    su1_l2p = 0
    su1_l1p = 0
    su1_l0p = 0
    if user_stat['su1'] > 0:
        su1_l4p = user_stat['su1_l4'] / user_stat['su1'] * 100
        su1_l3p = user_stat['su1_l3'] / user_stat['su1'] * 100
        su1_l2p = user_stat['su1_l2'] / user_stat['su1'] * 100
        su1_l1p = user_stat['su1_l1'] / user_stat['su1'] * 100
        su1_l0p = user_stat['su1_l0'] / user_stat['su1'] * 100

    su2_l4p = 0
    su2_l3p = 0
    su2_l2p = 0
    su2_l1p = 0
    su2_l0p = 0
    if user_stat['su2'] > 0:
        su2_l4p = user_stat['su2_l4'] / user_stat['su2'] * 100
        su2_l3p = user_stat['su2_l3'] / user_stat['su2'] * 100
        su2_l2p = user_stat['su2_l2'] / user_stat['su2'] * 100
        su2_l1p = user_stat['su2_l1'] / user_stat['su2'] * 100
        su2_l0p = user_stat['su2_l0'] / user_stat['su2'] * 100

    su3_l4p = 0
    su3_l3p = 0
    su3_l2p = 0
    su3_l1p = 0
    su3_l0p = 0
    if user_stat['su3'] > 0:
        su3_l4p = user_stat['su3_l4'] / user_stat['su3'] * 100
        su3_l3p = user_stat['su3_l3'] / user_stat['su3'] * 100
        su3_l2p = user_stat['su3_l2'] / user_stat['su3'] * 100
        su3_l1p = user_stat['su3_l1'] / user_stat['su3'] * 100
        su3_l0p = user_stat['su3_l0'] / user_stat['su3'] * 100

    su4_l4p = 0
    su4_l3p = 0
    su4_l2p = 0
    su4_l1p = 0
    su4_l0p = 0
    if user_stat['su4'] > 0:
        su4_l4p = user_stat['su4_l4'] / user_stat['su4'] * 100
        su4_l3p = user_stat['su4_l3'] / user_stat['su4'] * 100
        su4_l2p = user_stat['su4_l2'] / user_stat['su4'] * 100
        su4_l1p = user_stat['su4_l1'] / user_stat['su4'] * 100
        su4_l0p = user_stat['su4_l0'] / user_stat['su4'] * 100
        
    return templates.TemplateResponse(
                "general_pages/dashboard.html",
                {
                    "request": request,
                    "current_user": current_user.email,
                    "is_superuser": current_user.is_superuser,
                    #"scheme": request.url.scheme,
                    #"hostname": request.url.hostname,
                    #"port": request.url.port,
                    "url": url,
                    "invite_token": current_user.invite_token,
                    "level": current_user.level,
                    "balance": int(current_user.balance / 1000000),
                    "levelup_hold": int(current_user.levelup_hold / 1000000),
                    "levelup_p": int(current_user.levelup_hold / wanted_level_price * 100),
                    "next_level": wanted_level,
                    "next_level_price": int(wanted_level_price / 1000000),

                    "su1":     user_stat['su1'],
                    "su1_l4":  user_stat['su1_l4'],
                    "su1_l4p": su1_l4p,
                    "su1_l3":  user_stat['su1_l3'],
                    "su1_l3p": su1_l3p,
                    "su1_l2":  user_stat['su1_l2'],
                    "su1_l2p": su1_l2p,
                    "su1_l1":  user_stat['su1_l1'],
                    "su1_l1p": su1_l1p,
                    "su1_l0":  user_stat['su1_l0'],
                    "su1_l0p": su1_l0p,
                    
                    "su2":     user_stat['su2'],
                    "su2_l4":  user_stat['su2_l4'],
                    "su2_l4p": su2_l4p,
                    "su2_l3":  user_stat['su2_l3'],
                    "su2_l3p": su2_l3p,
                    "su2_l2":  user_stat['su2_l2'],
                    "su2_l2p": su2_l2p,
                    "su2_l1":  user_stat['su2_l1'],
                    "su2_l1p": su2_l1p,
                    "su2_l0":  user_stat['su2_l0'],
                    "su2_l0p": su2_l0p,

                    "su3":     user_stat['su3'],
                    "su3_l4":  user_stat['su3_l4'],
                    "su3_l4p": su3_l4p,
                    "su3_l3":  user_stat['su3_l3'],
                    "su3_l3p": su3_l3p,
                    "su3_l2":  user_stat['su3_l2'],
                    "su3_l2p": su3_l2p,
                    "su3_l1":  user_stat['su3_l1'],
                    "su3_l1p": su3_l1p,
                    "su3_l0":  user_stat['su3_l0'],
                    "su3_l0p": su3_l0p,

                    "su4":     user_stat['su4'],
                    "su4_l4":  user_stat['su4_l4'],
                    "su4_l4p": su4_l4p,
                    "su4_l3":  user_stat['su4_l3'],
                    "su4_l3p": su4_l3p,
                    "su4_l2":  user_stat['su4_l2'],
                    "su4_l2p": su4_l2p,
                    "su4_l1":  user_stat['su4_l1'],
                    "su4_l1p": su4_l1p,
                    "su4_l0":  user_stat['su4_l0'],
                    "su4_l0p": su4_l0p,

                    "l0_price": int(LEVELS_PRICES[0] / 1000000),
                    "l1_price": int(LEVELS_PRICES[1] / 1000000),
                    "l2_price": int(LEVELS_PRICES[2] / 1000000),
                    "l3_price": int(LEVELS_PRICES[3] / 1000000),
                    "l4_price": int(LEVELS_PRICES[4] / 1000000),


                    "system_address": tadr,
                    "system_network": settings.TRON_NETWORK
                }
    )
