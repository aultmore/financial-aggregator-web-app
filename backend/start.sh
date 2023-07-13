#!/bin/bash

. ./env/bin/activate

#gunicorn -b 0.0.0.0:8039 -w 2 -k uvicorn.workers.UvicornWorker main:app --daemon
gunicorn -b 0.0.0.0:8039 -w 2 -k uvicorn.workers.UvicornWorker main:app

