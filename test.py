from object_tracking import Detector, YOLOv7_track

#создается детектор
detector = Detector(classes = [0,1,2,3,4,5], use_gpu = True)
# и к нему подгружаются веса
detector.load_model("./weights/best-tiny-200.pt")

#создаем трекер работающий на SORT и передаем ему веса
tracker = YOLOv7_track(detector=detector, use_cuda =True)


# запустим трекинг видео/ стрима из youtube
tracker.track_video("https://youtu.be/C77Fddophmg", output = None) 

# аналогично можно запустить  трекинг записанного видео видео передав в качестве аргумента локальный адрес видео
# если в output указать директорию с именем файла, то там запишется видеотрекинг

# чтобы добавить действия в начале или в конце детекции отдельной машины
#  отредактируйте файл notify_tracker.py 