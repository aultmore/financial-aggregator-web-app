#config.py

import os
from dotenv import load_dotenv
from pathlib import Path


env_path = Path('.') / '.env'
if not os.path.exists(env_path):
    print("You must configure your .env file")
    raise AssertionError

load_dotenv(dotenv_path = env_path)


class Settings:
    PROJECT_NAME : str      = "EvaToken"
    PROJECT_VERSION : str   = "0.5"

    POSTGRES_USER : str     = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD       = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER : str   = os.getenv("POSTGRES_SERVER","localhost")
    POSTGRES_PORT : str     = os.getenv("POSTGRES_PORT",5432) # default postgres port is 5432
    POSTGRES_DB : str       = os.getenv("POSTGRES_DB","tdd")
    DATABASE_URL            = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    SECRET_KEY : str        = os.getenv("SECRET_KEY")
    ALGORITHM               = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 120   # TODO in minutes
    TEMP_TOKEN_EXPIRE_MINUTES = 3       # in minutes, temporary token (for password change etc)

    SUPERUSER_LEVEL         = 5

    DEBUG_CHECK_PASSWORD    = True     # TODO Comment out for release deployment

    # TRON Network Access
    TRONGRID_API_KEY        = "be561084-72d2-453c-af39-ef76204191a0"
    TRON_NETWORK            = "TRC20"
    #TRON_ADDRESS            = "TUCgp51TzSQCCN4fjWcMFabRbyFqfpmAB4"
    TRON_ADDRESS : str      = os.getenv("TRON_ADDRESS")
    TRON_ADDRESS_PRIV : str      = os.getenv("TRON_ADDRESS_PRIV")

    # Support/admin contacts
    EMAIL_FIN : str         = "evatoken@proton.me"

    # Debug parameters
    DBG_SKIP_EMAIL_CONFIRM  = os.getenv("DBG_SKIP_EMAIL_CONFIRM")
    DBG_SKIP_TRANSACTIONS_POLLING  = os.getenv("DBG_SKIP_TRANSACTIONS_POLLING")


settings = Settings()

LEVELS_PRICES = [
    0,                  # for level 0 (out of the game)
    100_000000,         # for level 1
    200_000000,         # for level 2
    800_000000,         # for level 3
    12800_000000,       # for level 4
    819200_000000,      # for level 5
    9999999_000000      # unreachable level
]
MAXIMUM_LEVEL = 5




class AppRuntime:
    last_ts : int = 0

appRuntime = AppRuntime()
