# -*- coding: UTF-8 -*-
from fastapi import FastAPI, Form
from fastapi.responses import StreamingResponse
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

import routes
from videostream import VideoStream

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(routes.router)