import numpy as np
from PIL import Image
from time import time
from time import sleep
import torch
import cv2
import serial
import os

try:
    os.mkdir("yolo_output")
except FileExistsError:
    pass

ser = serial.Serial('COM14', 115200)
infrared = serial.Serial('COM4', 115200)

# Model
model = torch.hub.load('yolov5-master', 'custom', path='yolov5-master/KelapaV2.pt', source='local')

cam = cv2.VideoCapture(0)

cv2.namedWindow("Live Camera Window")

img_counter = 0


while True:
    ret, frame = cam.read()
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("Live Camera Window", frame)

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break

    if k%256 == 32:
        # SPACE pressed
        img_name = "capture_img.png"
        cv2.imwrite(img_name, frame)
        print("{} written!".format(img_name))
        results = model(img_name)
        try:
            hasi_string = results.pandas().xyxy[0].round(3).round(2)['name'][0]
            #print(hasi_string)
        except:
            hasi_string = "0"
            print(hasi_string)
        '''
        try:
            results.save(save_dir='yolo_output/capture')
            #results.pandas().xyxy[0].round(3).round(2).to_excel("yolo_output/{}.xlsx".format(img_counter), index=False)
        except:
            pass
        '''
        img_counter += 1
        if hasi_string == 'Reject':
            ser.write("l".encode())
            print("Non-Edible: Tidak dibuang!")
            print()
        if hasi_string == "0":
            print()
        if hasi_string == 'Edible' or hasi_string == 'Reguler':
            ser.write("r".encode())
            #sleep(1.5)
            #ser.write("l".encode())
            print("Edible: dibuang!")
            print()
    if (infrared.inWaiting() > 0):
        baca = infrared.readline()
        print(baca)
        if baca == b'OBSTACLE\r\n':
        #if baca =='c':
            # Trigger 'OBSTACLE' from Serial
            img_name = "capture_img.png"
            cv2.imwrite(img_name, frame)
            print("{} written!".format(img_name))
            results = model(img_name)
            try:
                hasi_string = results.pandas().xyxy[0].round(3).round(2)['name'][0]
                #print(hasi_string)
            except:
                hasi_string = "0"
                print(hasi_string)
            '''
            try:
                results.save(save_dir='yolo_output/capture')
                #results.pandas().xyxy[0].round(3).round(2).to_excel("yolo_output/{}.xlsx".format(img_counter), index=False)
            except:
                pass
            '''
            img_counter += 1
            if hasi_string == 'Reject':
                #ser.write("r".encode())
                ser.write("l".encode())
                print("Non-Edible: Tidak dibuang!")
                print()
            if hasi_string == "0":
                print()
            if hasi_string == 'Edible' or hasi_string == 'Reguler':
                #ser.write("l".encode())
                #sleep(1.5)
                ser.write("r".encode())
                print("Edible: dibuang!")
                print()


ser.close()

cam.release()

cv2.destroyAllWindows()