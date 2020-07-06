import sys
import cv2
import time
import random
import pafy
import numpy as np
import torch

from model.yolov4.tool.utils import *
from model.yolov4.tool.torch_utils import *
from model.yolov4.tool.darknet2pytorch import Darknet
from model.deepsort import DeepSort
from model.utils import utils


class VideoStream(object):
    
    half = False
    device = 'cuda'
    
    model_path = 'model'
    model_weights_tracker = f'{model_path}/deepsort/deep/checkpoint/ckpt.t7'
    model_weights_detector = f'{model_path}/yolov4/weights/yolov4.weights'
    model_config_detector = f'{model_path}/yolov4/cfg/yolov4.cfg'
    coco_names = f'{model_path}/yolov4/data/coco.names'
    
    names = None
    colors = None
    
    tracker = None
    detector = None

    conf_thresh = 0.5
    nms_thresh = 0.4
    n_classes = None
    
    _video = None
    
    _h = 608 # detector input size
    _w = 608

    def __init__(self, url):
        video = pafy.new(url)
        best = video.getbest(preftype="mp4")
        playurl = best.url
        
        self._load_networks()
        
        self._video = cv2.VideoCapture()
        self._video.open(playurl)
        
        self.names = utils.load_classes(self.coco_names)
        self.n_classes = len(self.names)
        
#         fps = self._video.get(cv2.CAP_PROP_FPS)
#         w = int(self._video.get(cv2.CAP_PROP_FRAME_WIDTH))
#         h = int(self._video.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         self.vid_writer = cv2.VideoWriter('test.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

        
    def _load_networks(self):
        self.tracker = DeepSort(self.model_weights_tracker)
        self.detector = Darknet(self.model_config_detector)
        self.detector.load_weights(self.model_weights_detector)
        self.detector.to(self.device).eval()
        if self.half:
            self.detector.half()

        
    def process_stream(self):
        while (self._video.isOpened()):
            read_success, frame = self._video.read()
            
            if read_success:
                self.orig_height, self.orig_width = frame.shape[:2]
                
                # run Detection
                sized = cv2.resize(frame, (self.detector.width, self.detector.height))
                sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)

                pred = do_detect(self.detector, sized,
                                 self.conf_thresh, self.n_classes,
                                 self.nms_thresh, use_cuda=1)
                if self.half:
                    pred = pred.float()

                # process detections
                det = torch.FloatTensor(np.array(pred, dtype=np.float32))

                if det is not None and len(det):
                    det[:,0] *= self.orig_width
                    det[:,2] *= self.orig_width
                    det[:,1] *= self.orig_height
                    det[:,3] *= self.orig_height

                    bbox_xywh = []
                    confs = []

                    # track detections
                    for i, (*xyxy, conf, cls) in enumerate(det):
                        bbox_left = xyxy[0] - xyxy[2] / 2.0
                        bbox_top = xyxy[1] - xyxy[3] / 2.0
                        bbox_w = xyxy[2]
                        bbox_h = xyxy[3]
                        x_c, y_c, bbox_w, bbox_h = utils.bbox_rel(self.orig_width,
                                                                  self.orig_height,
                                                                  bbox_left,
                                                                  bbox_top,
                                                                  bbox_w,
                                                                  bbox_h)
                        obj = [x_c, y_c, bbox_w, bbox_h]
                        bbox_xywh.append(obj)
                        confs.append([conf.item()])
                        label = '%s %.2f' % (self.names[int(cls)], conf)

                        try:
                            outputs = self.tracker.update((torch.Tensor(bbox_xywh)),
                                                      (torch.Tensor(confs)),
                                                      frame)
                            if len(outputs) > 0:
                                bbox_xyxy = outputs[:, :4]
                                identities = outputs[:, -1]
                                frame = utils.draw_boxes(frame, bbox_xyxy, identities)
                        except:
                            continue

#                 self.vid_writer.write(frame)
                    
                encode_success, jpeg = cv2.imencode('.jpg', frame)
                frame = jpeg.tobytes()
                print(f'yield frame len(det)={len(det)}')
                yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

            
    def _get_frame(self):
        success, image = self._video.read()
        ret, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    
    def stream_raw_video(self):
        while True:
            frame = self._get_frame()
            yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
