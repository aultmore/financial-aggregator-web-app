from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from core.config import settings, appRuntime
#from apis.general_pages.route_homepage import general_pages_router
from db_session import engine
from db_model import Base

from apis.base import api_router
from webapps.base import api_router as webapps_router

import time


def include_router(app):
    app.include_router(api_router)
    app.include_router(webapps_router)


def configure_static(app):
    app.mount("/static", StaticFiles(directory="static"), name="static")


def create_tables():
    print("create_tables")
    Base.metadata.create_all(bind=engine)


def load_last_timestamp(): # TODO Add it to DB
    try:
        with open("last_ts.txt", mode="r") as file1:
            s = file1.readline()
            file1.close()
            appRuntime.last_ts = int(s)
    except:
        appRuntime.last_ts = 0
    print("last timestamp loaded:", appRuntime.last_ts)


def start_application():
    load_last_timestamp()
    create_tables()
    app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)
    include_router(app)
    configure_static(app)
    
    if settings.DBG_SKIP_TRANSACTIONS_POLLING is not None:
        print("!!! WARNING !!! Debug mode is ON")

    if settings.DBG_SKIP_EMAIL_CONFIRM is not None:
        print("! Email confirmation is OFF")
    
    return app


app = start_application()
