from starlette.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from videostream import VideoStream
from fastapi import APIRouter, Request, Form

router = APIRouter()

templates = Jinja2Templates(directory="templates")
        
@router.get("/")
async def main(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@router.post("/stream")
async def stream(request: Request, url: str = Form(...), action: str = Form(...)):
    if action == 'yolov4':
        track = False
    elif action == 'yolov4 + deepsort':
        track = True
    
    return StreamingResponse(VideoStream(url).process_stream(track=track),
                             media_type="multipart/x-mixed-replace; boundary=frame")