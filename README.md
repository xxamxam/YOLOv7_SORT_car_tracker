# YOLOv7_SORT_car_tracker
Здесь представлен код реализации трекера машин с  YOLOv7 + SORT.

YOLOv7 https://github.com/WongKinYiu/yolov7

SORT https://github.com/abewley/sort


В object_tracking: 

-> YOLOv7 --- для детекции

-> sort --- трекер SORT

-> pafy_fix --- исправленный pafy в связи с отключением дизлайков на YouTube (https://github.com/mps-youtube/pafy ), нужен для чтения видеопотока с YouTube

-> detection_helpers.py --- наработка над yolov7 для удобства вызова

-> notify_tracker.py --- трекер для уведомлений

-> threads.py --- многопоточность

-> bridge_wrapper.py --- код объединения моделей
