from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
from datetime import datetime, timedelta

from schema_users import UserCreate
from db_model import User
from core.config import settings
from core.hashing import Hasher
from core.security import create_access_token

import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText




async def send_confirmation_email(user: User, url):
    token = user.invite_token

    # Create the message (HTML). TODO Set evatoken url!
    text = f"""\
    Добро пожаловать в EvaToken
    <br/>
    Подтвердите свой email, нажав
    <a href="{url}/confirm_email/{token}">сюда</a>
    <br/>
    Ждем вас в игре.
    """
    await send_email(to_address=user.email, text=text)


async def send_passwordchange_email(email, token, url):
    # Create the message (HTML). TODO Set evatoken url!
    text = f"""\
    <h2>EvaToken - Сброс пароля</h2>
    Для изменения пароля перейдите по
    <a href="{url}{token}">ссылке.</a>
    """
    await send_email(to_address=email, text=text)


async def send_withdraw_email(user: User, to_adddress, amount):
    # Create the message (HTML). TODO Set evatoken url!
    text = f"""\
    <h2>Запрос на вывод токенов</h2>
    <p>Пользователь:{user.email}</p>
    <p>Адрес кошелька:{to_adddress}</p>
    <p>Сумма:{amount}</p>
    """
    await send_email(to_address=settings.EMAIL_FIN, text=text)


async def send_email(to_address, text):
    from_address = "confirm.evatoken@evatoken.net"

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Email from EvaToken"
    msg['From'] = from_address
    msg['To'] = to_address

    # Record the MIME type - text/html.
    part1 = MIMEText(text, 'html')

    # Attach parts into message container
    msg.attach(part1)

    # Credentials
    username = 'confirm.evatoken@gmail.com'  
    password = 'gscbefgxuziseisn'

    # Sending the email
    ## note - this smtp config worked for me, I found it googling around, you may have to tweak the # (587) to get yours to work
    server = smtplib.SMTP('smtp.gmail.com', 587) 
    server.ehlo()
    server.starttls()
    server.login(username, password)  
    server.sendmail(from_address, to_address, msg.as_string())  
    server.quit()


async def create_new_user(user: UserCreate, db: Session):
    user = User(
            email = user.email,
            hashed_password = Hasher.get_password_hash(user.password),
            tlg_username = user.tlg_username,
            is_adult = user.is_adult,
            is_agreed = user.is_agreed,
            is_confirmed = user.is_confirmed,
            is_superuser = user.is_superuser,
            level = user.level,
            balance = 0,
            levelup_hold = 0,
            date_registered = datetime.now(),
            ref_user = user.ref_user,
            wrong_logins = 0,
            wrong_login_ts = datetime.min
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # create invite token for new users
    user.invite_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id
        },
        expires_delta = timedelta(weeks=530)  # 10 years expiration
    )
    db.commit()

    return user


def get_user(db: Session, id: int = 0, email: str = None):
    if email is not None:
        user = db.query(User).filter(func.lower(User.email) == func.lower(email)).first()
    else:
        user = db.query(User).filter(User.id == id).first()
    return user


def get_boss_user(user_id: int, wanted_level: int, db: Session):
    ref_user = None
    ref_id = user_id
    #user = db.query(User).filter(User.id == user_id).first()
    #ref_id = user.ref_user
    while True:
        ref_user = db.query(User).filter(User.id == ref_id).first()
        if ref_user.ref_user == 0:
            break
        if ref_user.level >= wanted_level:
            break
        ref_id = ref_user.ref_user
    return ref_user


def authenticate_user(email: str, password: str, db: Session):
    user = get_user(email=email, db=db)

    if not user:
        return False

    if datetime.now() < user.wrong_login_ts:
        raise Exception("Слишком много попыток входа!")

    if not Hasher.verify_password(password, user.hashed_password):
        if user.wrong_logins == 0:
            user.wrong_login_ts = datetime.now()
        user.wrong_logins += 1
        db.commit()

        if user.wrong_logins > 3:
            dt = datetime.now() - user.wrong_login_ts
            if dt.total_seconds() < 60:
                user.wrong_login_ts = datetime.now() + timedelta(minutes=3)
                db.commit()
                raise Exception("Слишком много попыток входа! Подождите 3 минуты.")
        return False
    else:
        user.wrong_logins = 0
        user.wrong_login_ts = datetime.min
        db.commit()

    return user


def find_user(email: str, db: Session):
    user = get_user(email=email, db=db)
    #print(user)
    if not user:
        return False
    return user


def set_temp_token_for_user(email: str, temp_token: str, db: Session):
    user = get_user(email=email, db=db)
    if not user:
        return None
    user.temp_token = temp_token
    #print("user.temp_token=", temp_token)
    db.commit()
    db.refresh(user)


def user_change_password(email: str, password: str, db: Session):
    user = get_user(email=email, db=db)
    if not user:
        return None
    #print("new password=", password)
    user.hashed_password = Hasher.get_password_hash(password)
    db.commit()

def user_update_balance(email: str, amount: int, db: Session):
    user = get_user(email=email, db=db)
    if not user:
        return None
    user.balance = user.balance - amount
    db.commit()


#
# Builds the user connection network (tree)
#
def build_user_network(ref_user_id, db: Session):
    users = db.query(User).filter(User.ref_user == ref_user_id).all()
    res = []
    for u in users:
        l = build_user_network(u.id, db)
        if l:
            u.user_network = l
        res.append(u)
    return res


#
# Returns the user connection network (tree)
#
def list_user_network(ref_user_email: str, db: Session):
    user = get_user(email=ref_user_email, db=db)
    if not user:
        return None
    user.user_network = build_user_network(user.id, db)
    return user


#
# Calculates the user network levels - which levels have all the connected users
#
def calc_user_network(ref_user_id, levels, db: Session):
    users = db.query(User).filter(User.ref_user == ref_user_id).all()
    for u in users:
        if str(u.level) in levels:
            levels[str(u.level)] += 1
        else:
            levels[str(u.level)] = 1

        l = calc_user_network(u.id, levels, db)
        
    return levels


def user_network_levels(user_email: str, db: Session):
    user = get_user(email=user_email, db=db)
    if not user:
        return None
    levels = {}
    user.user_network_levels = calc_user_network(user.id, levels, db)
    return user.user_network_levels


#
# Collects user statistics TODO Optimize it!!!
# user.ref:    number of users, number of level == 1
# user.ref-1:  number of users, number of level == 2
# user.ref-2:  number of users, number of level == 3
# user.ref-3:  number of users, number of level == 4
#
def get_user_stats(user: User, db: Session):
    user_stat = {}

    sub_users_1 = db.query(User).filter(User.ref_user == user.id).all()

    user_count = 0
    l0_count = 0
    l1_count = 0
    l2_count = 0
    l3_count = 0
    l4_count = 0
    sub_users_2 = []
    for u in sub_users_1:
        user_count += 1
        if u.level == 0: l0_count += 1
        elif u.level == 1: l1_count += 1
        elif u.level == 2: l2_count += 1
        elif u.level == 3: l3_count += 1
        elif u.level == 4: l4_count += 1
        sub_users_2 += db.query(User).filter(User.ref_user == u.id).all()
    user_stat['su1'] = user_count
    user_stat['su1_l0'] = l0_count
    user_stat['su1_l1'] = l1_count
    user_stat['su1_l2'] = l2_count
    user_stat['su1_l3'] = l3_count
    user_stat['su1_l4'] = l4_count
    
    user_count = 0
    l0_count = 0
    l1_count = 0
    l2_count = 0
    l3_count = 0
    l4_count = 0
    sub_users_3 = []
    for u in sub_users_2:
        user_count += 1
        if u.level == 0: l0_count += 1
        elif u.level == 1: l1_count += 1
        elif u.level == 2: l2_count += 1
        elif u.level == 3: l3_count += 1
        elif u.level == 4: l4_count += 1
        sub_users_3 += db.query(User).filter(User.ref_user == u.id).all()
    user_stat['su2'] = user_count
    user_stat['su2_l0'] = l0_count
    user_stat['su2_l1'] = l1_count
    user_stat['su2_l2'] = l2_count
    user_stat['su2_l3'] = l3_count
    user_stat['su2_l4'] = l4_count

    user_count = 0
    l0_count = 0
    l1_count = 0
    l2_count = 0
    l3_count = 0
    l4_count = 0
    sub_users_4 = []
    for u in sub_users_3:
        user_count += 1
        if u.level == 0: l0_count += 1
        elif u.level == 1: l1_count += 1
        elif u.level == 2: l2_count += 1
        elif u.level == 3: l3_count += 1
        elif u.level == 4: l4_count += 1
        sub_users_4 += db.query(User).filter(User.ref_user == u.id).all()
    user_stat['su3'] = user_count
    user_stat['su3_l0'] = l0_count
    user_stat['su3_l1'] = l1_count
    user_stat['su3_l2'] = l2_count
    user_stat['su3_l3'] = l3_count
    user_stat['su3_l4'] = l4_count

    user_count = 0
    l0_count = 0
    l1_count = 0
    l2_count = 0
    l3_count = 0
    l4_count = 0
    for u in sub_users_4:
        user_count += 1
        if u.level == 0: l0_count += 1
        elif u.level == 1: l1_count += 1
        elif u.level == 2: l2_count += 1
        elif u.level == 3: l3_count += 1
        elif u.level == 4: l4_count += 1
    user_stat['su4'] = user_count
    user_stat['su4_l0'] = l0_count
    user_stat['su4_l1'] = l1_count
    user_stat['su4_l2'] = l2_count
    user_stat['su4_l3'] = l3_count
    user_stat['su4_l4'] = l4_count

    return user_stat
