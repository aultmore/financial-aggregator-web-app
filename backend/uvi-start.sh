#!/bin/bash

. ../env/bin/activate

#uvicorn main:app --daemon
uvicorn main:app

