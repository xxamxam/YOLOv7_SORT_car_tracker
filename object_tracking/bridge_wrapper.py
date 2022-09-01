'''
A Module which binds Yolov7 repo with sort/sort with modifications
'''

import os

import cv2
import numpy as np
import matplotlib.pyplot as plt

from notify_tracker import *
# sort imports
from sort.sort import Sort
# load configuration for object detector
from time import time
from threads import *
 
import pafy_fix as pafy


def video_getter(vid, skip_frames):
    frame_num = 0
    while True:
        ret_val, frame = vid.read()
        if skip_frames and not frame_num % skip_frames:
            continue
        frame_num += 1
        if not ret_val:
            print("video has ended or failed")
            break
        yield (frame_num, frame)

def detect(detector, getter):
    for frame_num, frame in getter:
        rez = detector.detect(frame.copy(), plot_bb = False)
        if rez is None:
            rez = []
        yield (frame_num, rez, frame)
        
class Track_notify_write():
    def __init__(self, tracker, notify_tracker, out):
        self.tracker = tracker
        self.notify_tracker = notify_tracker
        self.out = out
    def __call__(self, inp):
        frame_num, x, frame = inp
        bboxes = []
        scores = []
        detections = []    

        if len(x) != 0:
            detections = self.tracker.update(x)
        if len(detections) != 0:
            idx = detections[:, 4]
            self.notify_tracker.update(idx, frame_num)
            cmap = plt.get_cmap('tab20b')
            colors = [cmap(i)[:3] for i in np.linspace(0, 1, 20)]
            for det in detections:
                bbox = det[:4]
                track_id = det[4]
                # should we insert the correct name here?
                class_name = "car"

                color = colors[int(track_id) % len(colors)]
                cv2.rectangle(frame, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), color, 2)
                cv2.rectangle(frame, (int(bbox[0]), int(bbox[1]-30)), (int(bbox[0])+(len(class_name)+len(str(track_id)))*17, int(bbox[1])), color, -1)
                cv2.putText(frame, class_name + " : " + str(track_id),(int(bbox[0]), int(bbox[1]-11)),0, 0.6, (255,255,255),1, lineType=cv2.LINE_AA)                      
            
        result = np.asarray(frame)
        if self.out is not None:
            self.out.write(result)
  



class YOLOv7_track:
    '''
    Class to Wrap ANY detector  of YOLO type with SORT
    '''
    def __init__(self, detector, reID_model_path:str = None, notify_tracker = Notify_tracker(),  max_cosine_distance:float=0.4, nn_budget:float=None, nms_max_overlap:float=1.0, use_cuda: bool = False, print_: bool = False):
        '''
        args: 
            reID_model_path: Path of the model which uses generates the embeddings for the cropped area for Re identification
            detector: object of YOLO models or any model which gives you detections as [x1,y1,x2,y2,scores, class]
            max_cosine_distance: Cosine Distance threshold for "SAME" person matching
            nn_budget:  If not None, fix samples per class to at most this number. Removes the oldest samples when the budget is reached.
            nms_max_overlap: Maximum NMs allowed for the tracker
            coco_file_path: File wich contains the path to coco naames
        '''
        self.detector = detector
        self.nms_max_overlap = nms_max_overlap
        self.print_ = print_
#TODO : сопоставление меток классов и их имен
        self.class_names = ["1"] #read_class_names()
        
        self.notify_tracker = notify_tracker
        # initialize sort
        self.sort = Sort(max_age = 10)
   

    def track_video(self, video:str, output:str, skip_frames:int=0, show_live:bool=False, count_objects:bool=False, verbose:int = 0):
        
        
        if video.startswith("https://youtu.be"):
# тут выбирается видеопоток с ютуба                     
            vPafy = pafy.new(video)
            streams = vPafy.streams
            for i, s in enumerate(streams):
                print(f"{i}) {s}")  
            while True:
                print("выберите номер источника:")
                numm = input()
                try:
                    numm = int(numm)
                except:
                    print("введите число!! чтобы выйти нажмите Ctrl + C")
                    continue
                if 0 <= numm < len(streams):
                    play = streams[numm]
                    break
                else:
                    print("вы ввели неправильное число. чтобы выйти нажмите Ctrl + C")
                            
            vid = cv2.VideoCapture(play.url)
        else:
            try:
                vid = cv2.VideoCapture(int(video))
            except:
                vid = cv2.VideoCapture(video)

        out = None
        if output:
            width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))  # by default VideoCapture returns float instead of int 
            height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(vid.get(cv2.CAP_PROP_FPS))
            codec = cv2.VideoWriter_fourcc(*"XVID")
            out = cv2.VideoWriter(output, codec, fps, (width, height))

        getter = video_getter(vid, skip_frames)
        detector = detect(self.detector, getter)
        tracker = Track_notify_write(self.sort, self.notify_tracker, out)

        start_time = time()
        thr = Thread_convey([detector, tracker])
        frames = thr.start()
        print(f"tracked {frames} frames in {time() - start_time} seconds, or {frames / (time() - start_time)} fps")