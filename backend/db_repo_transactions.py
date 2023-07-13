from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from datetime import datetime

from core.config import LEVELS_PRICES, MAXIMUM_LEVEL
from core.hashing import Hasher
from db_model import User, Transaction
from schema_transactions import TransactionRecord
from db_repo_users import get_user, get_boss_user



#
# TODO TRON network daemon here
# It generates/crates the transactions for the main logic
#

#
# Processes payment and level up logic
#
def try_user_level_up(user_id: int, amount: int, ref_transaction: id, db: Session):

    # Get user by 'user_id'
    user = get_user(id=user_id, db=db)
    
    if user.level >= MAXIMUM_LEVEL:
        
        # No more level ups
        print("!!!! MAXIMUM LEVEL REACHED !!!!!")
        
        # System.balance -= amount
        #create_transaction_exp(to_user_email=user.email, amount=-amount, db=db)
        
        # Add amount to user balance
        create_transaction_balance(
                    user_email=user.email,
                    amount=amount,
                    ref_transaction=ref_transaction,
                    db=db)
        user.balance += amount
        
        db.commit()

    else:

        wanted_level = user.level + 1
        wanted_level_price = LEVELS_PRICES[wanted_level]

        # users levelup holds are not countable in the total balance
        # do not create system.balance expense transaction
        create_transaction_to_hold(
                    user=user,
                    amount=amount,
                    ref_transaction=ref_transaction,
                    db=db)
        user.levelup_hold += amount         # hold level up price
        db.commit()

        print("***       wanted_level:", wanted_level)
        print("*** wanted_level_price:", wanted_level_price)
        print("***               user:", user.email)

        if user.levelup_hold >= wanted_level_price: # User can up the level

            print("^^^ User buys new level:", wanted_level)
            levelup_change = user.levelup_hold - wanted_level_price

            # If amount is the money for level+2 (3rd level from 2st level,
            # 4th level from 2nd level) we keep the change in user's hold
            if amount == LEVELS_PRICES[wanted_level+1]:
                levelup_change = 0

            #
            # User buys the new level
            #

            # Get money from user's HOLD
            create_transaction_from_hold(
                            user=user,
                            amount=wanted_level_price,
                            ref_transaction=ref_transaction,
                            db=db)
            user.levelup_hold -= wanted_level_price

            # If there is a change (HOLD > wanted_level_price) it goes to user balance
            if levelup_change > 0:
                print("    Levelup change:", levelup_change)
                create_transaction_from_hold(
                            user=user,
                            amount=levelup_change,
                            ref_transaction=ref_transaction,
                            db=db)
                user.levelup_hold -= levelup_change

                create_transaction_balance(
                            user=user,
                            amount=levelup_change,
                            ref_transaction=ref_transaction,
                            db=db)
                user.balance += levelup_change

            # User gets the new level
            user_level = user.level # to use it later in the transaction record
            user.level = wanted_level
            db.commit()

            #
            # Find where to buy the new level
            #
            ref_user = get_user(id=user.ref_user, db=db)
            for n in range(wanted_level-1):
                if ref_user.ref_user == 0:
                    break
                ref_user = get_user(id=ref_user.ref_user, db=db)

            # Level Up Transaction Record
            create_transaction_levelup(
                            from_user=ref_user,
                            to_user=user,
                            user_level=user_level,
                            wanted_level=wanted_level,
                            ref_transaction=ref_transaction,
                            db=db)

            print("--- Buy level", wanted_level, "from user", ref_user.email)

            if wanted_level < ref_user.level:  # Ref user can sell me the level
                # System.balance -= amount
                #print("vvv System transfers money to ref_user: ", -amount)
                #create_transaction_exp(to_user_email=ref_user.email, amount=-wanted_level_price, db=db)
                # Ref user balance += amount
                print("^^^ Ref user sells new level, ref_user.balance +=", wanted_level_price)
                create_transaction_balance(
                            user=ref_user,
                            amount=wanted_level_price,
                            ref_transaction=ref_transaction,
                            db=db)
                ref_user.balance += wanted_level_price
                db.commit()

            elif wanted_level >= ref_user.level:  # Ref user can sell me the level
                print("^^^ Ref user sells new level, tokens hold:", wanted_level_price)
                try_user_level_up(
                            user_id=ref_user.id,
                            amount=wanted_level_price,
                            ref_transaction=ref_transaction,
                            db=db)
        
    return

#
# Processes tokens income
# Called from the TRON network worker
#
def process_income(record: Transaction, db: Session):
    try_user_level_up(
                user_id=record.user_id,
                amount=record.amount,
                ref_transaction=record.id,
                db=db)
    return




def check_transaction_for_user(user: User, txid: str, db: Session):
    #print("check_transaction_for_user:")
    #print("    ", user.email)
    #print("    ", txid)
    tr = db.query(Transaction).filter(Transaction.hash_string == txid).first()
    if tr is not None:
        if tr.user_email == "":
            print("transaction:", tr)
            tr.result = "DONE"      # TODO use results contants
            tr.user_email = user.email
            tr.user_id = user.id
            db.commit()
            db.refresh(tr)
            process_income(record=tr, db=db)
    # TODO Add not found case for transaction




# TODO This functions is being called from the TRON wallet API
def create_new_transaction(record: TransactionRecord, user_id, db: Session):

    user = get_user(email=record.user_email, db=db)
    if user is None:
        print("transaction user not found")
        record.result = "USER_NOT_FOUND"
        record.user_id = 0
    else:
        print("transaction for user: ", user.id, user.email)
        record.user_id = user.id

    tr = Transaction(
        hash_string = record.hash_string,
        ref_transaction = record.ref_transaction,
        operation = record.operation,
        result = record.result,
        block_ts = record.block_ts,
        ts = record.ts,
        amount = record.amount,
        owner_address = record.owner_address,
        to_address = record.to_address,
        user_email = record.user_email,
        user_id = record.user_id
    )

    # TODO Make this code in critical section

    try:
        db.add(tr)
        db.flush()
    except IntegrityError as e:
        db.rollback()
        #print("IntegrityError:", str(e))
        tr = None
    else:
        db.commit()
        db.refresh(tr)

    return tr


def create_transaction_inc(user: User, amount: int, ref_transaction: int, db: Session):
    #user = get_user(email=from_user_email, db=db)
    tr = None
    if user is not None:
        tm = datetime.now()
        record = TransactionRecord(
            hash_string = Hasher.get_transaction_hash(str(tm)),
            ref_transaction = ref_transaction,
            operation = "INC",     # TODO operations names
            result = "DONE",    # TODO Check
            block_ts = tm,
            ts = tm,
            amount = amount,
            owner_address = user.email,
            to_address = "system", # TODO system address
            user_email = user.email,
            user_id = user.id
        )
        tr = create_new_transaction(record=record, user_id=record.user_id, db=db)
    return tr


def create_transaction_exp(user: User, amount: int, ref_transaction: int, db: Session):
    #user = get_user(email=to_user_email, db=db)
    tr = None
    if user is not None:
        tm = datetime.now()
        record = TransactionRecord(
            hash_string = Hasher.get_transaction_hash(str(tm)),
            ref_transaction = ref_transaction,
            operation = "EXP",     # TODO operations names
            result = "DONE",    # TODO Check
            block_ts = tm,
            ts = tm,
            amount = amount,
            owner_address = "system",
            to_address = user.email, # TODO system address
            user_email = user.email,
            user_id = user.id
        )
        tr = create_new_transaction(record=record, user_id=record.user_id, db=db)
    return tr


def create_transaction_levelup(from_user: User, to_user: User,
                               user_level: int, wanted_level: int,
                               ref_transaction: int, db: Session):
    tr = None
    if to_user is not None:
        record = None
        tm = datetime.now()
        record = TransactionRecord(
            hash_string = Hasher.get_transaction_hash(str(tm)),
            ref_transaction = ref_transaction,
            operation = f"LEVEL_UP_{user_level}_{wanted_level}",
            result = "DONE",            # TODO Results names
            block_ts = tm,
            ts = tm,
            amount = 0,
            owner_address = from_user.email,
            to_address = to_user.email, # TODO system address
            user_email = to_user.email,
            user_id = to_user.id
        )
        tr = create_new_transaction(record=record, user_id=record.user_id, db=db)
    return tr


def create_transaction_to_hold(user: User, amount: int, ref_transaction: int, db: Session):
    #user = get_user(email=user_email, db=db)
    tr = None
    if user is not None:
        record = None
        tm = datetime.now()
        record = TransactionRecord(
            hash_string = Hasher.get_transaction_hash(str(tm)),
            ref_transaction = ref_transaction,
            operation = "TO_HOLD",     # TODO operations names
            result = "DONE",            # TODO Results names
            block_ts = tm,
            ts = tm,
            amount = -amount,
            owner_address = "system",
            to_address = user.email, # TODO system address
            user_email = user.email,
            user_id = user.id
        )
        tr = create_new_transaction(record=record, user_id=record.user_id, db=db)
    return tr



def create_transaction_from_hold(user: User, amount: int, ref_transaction: int, db: Session):
    #user = get_user(email=user_email, db=db)
    tr = None
    if user is not None:
        record = None
        tm = datetime.now()
        record = TransactionRecord(
            hash_string = Hasher.get_transaction_hash(str(tm)),
            ref_transaction = ref_transaction,
            operation = "FROM_HOLD",     # TODO operations names
            result = "DONE",            # TODO Results names
            block_ts = tm,
            ts = tm,
            amount = amount,
            owner_address = user.email,
            to_address = "system", # TODO system address
            user_email = user.email,
            user_id = user.id
        )
        tr = create_new_transaction(record=record, user_id=record.user_id, db=db)
    return tr



def create_transaction_balance(user: User, amount: int, ref_transaction: int, db: Session):
    #user = get_user(email=user_email, db=db)
    tr = None
    if user is not None:
        record = None
        tm = datetime.now()
        if amount >= 0:
            record = TransactionRecord(
                hash_string = Hasher.get_transaction_hash(str(tm)),
                ref_transaction = ref_transaction,
                operation = "TO_BALANCE",       # TODO operations names
                result = "DONE",                # TODO Results names
                block_ts = tm,
                ts = tm,
                amount = amount,
                owner_address = "system",
                to_address = user.email,        # TODO system address
                user_email = user.email,
                user_id = user.id
            )
        else:
            record = TransactionRecord(
                hash_string = Hasher.get_transaction_hash(str(tm)),
                ref_transaction = ref_transaction,
                operation = "FROM_BALANCE",     # TODO operations names
                result = "TO_BE_DONE",          # TODO Results names
                block_ts = tm,
                date = tm,
                amount = amount,
                owner_address = user.email,
                to_address = "external",        # TODO User external address
                user_email = user.email,
                user_id = user.id
            )
        tr = create_new_transaction(record=record, user_id=record.user_id, db=db)
    return tr


def create_transaction_withdraw(user: User, amount: int, to_address: str, db: Session):
    tr = None
    if user is not None:
        record = None
        tm = datetime.now()
        record = TransactionRecord(
            hash_string = Hasher.get_transaction_hash(str(tm)),
            ref_transaction = 0,
            operation = "WITHDRAW",         # TODO operations names
            result = "TO_BE_DONE",          # TODO Results names
            block_ts = tm,
            ts = tm,
            amount = amount,
            owner_address = "system",
            to_address = to_address,
            user_email = user.email,
            user_id = user.id
        )
        tr = create_new_transaction(record=record, user_id=record.user_id, db=db)
    return tr
