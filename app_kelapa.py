import numpy as np
from PIL import Image
from time import time
from time import sleep
import torch
import cv2
# import serial
import os
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from PIL import ImageTk, Image
import csv
from datetime import datetime

# ser = serial.Serial('COM14', 115200)
# infrared = serial.Serial('COM4', 115200)

# Load the model
model = torch.hub.load('yolov5', 'custom', path='models/KelapaV3_YOLOv5.pt', source='local')

# Declare variables
now = datetime.now()
csv_file_path = "log_kelapa_{}.csv".format(now.strftime("%Y-%m-%d-%S"))
total_counter = 0
standar_counter = 0
nonStandar_counter = 0
notDefined_counter = 0

def show_alert(subject, message):
    messagebox.showinfo(subject, message)

def update_text(formatted_datetime, hasil, class_counter, total_counter):
    text_area.configure(state='normal')
    text_area.insert("end", "\n Waktu: {} \n Kualitas: {} \n Class Counter: {} \n Total Counter: {} \n"
                     .format(formatted_datetime, hasil, class_counter, total_counter))
    text_area.configure(state='disabled')
    text_area.see("end")
    
def save_to_csv():
    # Get the current contents of the text_area widget
    text_contents = text_area.get("1.0", "end-1c")

    # Extract the values from the text contents
    lines = text_contents.split("\n")
    data = [line.split(": ")[1] for line in lines if line]

    # Define the header row and data rows
    header_row = ["Waktu", "Kualitas", "Class Counter", "Total Counter"]
    data_rows = [data[i:i+4] for i in range(0, len(data), 4)]

    # Write the contents to the CSV file
    with open(csv_file_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header_row)  # Write header row
        writer.writerows(data_rows)  # Write data rows
    
def update_frame():
    global video_capture
    global total_counter
    global standar_counter
    global nonStandar_counter
    global notDefined_counter
    if video_capture is not None:
        # Read the video frame
        ret, frame = video_capture.read()
        if ret:
            # Convert the frame to RGB format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create an ImageTk object
            image_tk = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))

            # Update the label with the new image
            image_label.configure(image=image_tk)
            image_label.image = image_tk
            
            # Schedule the next frame update
            image_label.after(120, update_frame)

            # Resize the frame to a compatible size for YOLOv5
            resized_frame = cv2.resize(frame, (640, 640))
            
            # Get the results and print
            # Automatically capture the frame
            img_name = "capture_img.png"
            cv2.imwrite(img_name, resized_frame)
            results = model(img_name)
                       
            # Get the current datetime
            now = datetime.now()
            # Format the datetime as desired
            formatted_datetime = now.strftime("%Y-%m-%d-%S.%f")
            
            try:
                check = results.pandas().xyxy[0].round(3).round(2)['name'][0]
            except:
                check = "not_defined"
                
            if check == 'Standar':
                hasil = 'Standar'
                standar_counter += 1
                total_counter += 1
                # Update the text area
                update_text(formatted_datetime, hasil, standar_counter, total_counter)
                # Save to CSV
                save_to_csv()
                # SERIAL ACTIONS
            elif check == 'NonStandar':
                hasil = 'NonStandar'
                nonStandar_counter += 1
                total_counter += 1
                # Update the text area
                update_text(formatted_datetime, hasil, nonStandar_counter, total_counter)
                # Save to CSV
                save_to_csv()
                # SERIAL ACTIONS
            elif check == 'not_defined':
                hasil = 'not_defined'
                notDefined_counter += 1
                total_counter += 1
                # Update the text area
                update_text(formatted_datetime, hasil, notDefined_counter, total_counter)
                # Save to CSV
                save_to_csv()
                # SERIAL ACTIONS
                
            # if (infrared.inWaiting() > 0):
            #         baca = infrared.readline()
            #         print(baca)
            #         if baca == b'OBSTACLE\r\n':
            #         #if baca =='c':
            #             # Trigger 'OBSTACLE' from Serial
            #             img_name = "capture_img.png"
            #             cv2.imwrite(img_name, frame)
            #             print("{} written!".format(img_name))
            #             text_area.insert("end", "{} written! \n".format(img_name))
            #             results = model(frame_rgb)
            #             try:
            #                 hasil_string = results.pandas().xyxy[0].round(3).round(2)['name'][0]
            #                 #print(hasil_string)
            #             except:
            #                 hasil_string = "0"
            #                 print(hasil_string)
            #                 text_area.insert("end", hasil_string)
            #             '''
            #             try:
            #                 results.save(save_dir='yolo_output/capture')
            #                 #results.pandas().xyxy[0].round(3).round(2).to_excel("yolo_output/{}.xlsx".format(img_counter), index=False)
            #             except:
            #                 pass
            #             '''
            #             img_counter += 1
            #             if hasil_string == 'Reject':
            #                 #ser.write("r".encode())
            #                 ser.write("l".encode())
            #                 print("Non-Edible: Tidak dibuang!")
            #                 print()
            #                 text_area.insert("end", "Non-Edible: Tidak dibuang!")
            #             if hasil_string == "0":
            #                 print()
            #             if hasil_string == 'Edible' or hasil_string == 'Reguler':
            #                 #ser.write("l".encode())
            #                 #sleep(1.5)
            #                 ser.write("r".encode())
            #                 print("Edible: dibuang!")
            #                 print()
            #                 text_area.insert("end", "Edible: dibuang!")
    else:
        # Display the placeholder image if no frame is available
        image_label.configure(image=placeholder_image)
        image_label.image = placeholder_image

def start_detection():
    global video_capture
    if video_capture is None:
        # Set the desired resolution
        width = 640  # Adjust the width as desired
        height = 640  # Adjust the height as desired
        
        # Open the video capture device with the desired resolution
        video_capture = cv2.VideoCapture(1)  # Use 0 for the default camera
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        # Update the frame
        update_frame()
    else:
        show_alert("Information", "Detection is already running")
    

def stop_detection():
    global video_capture
    if video_capture is not None:
        # Stop the camera
        video_capture.release()
        video_capture = None
        
        # Update the frame
        update_frame()
    else:
        show_alert("Information", "Detection is not running")

# Create the main window
window = tk.Tk()
window.title("Coconut Detection GUI")
video_capture = None

# Create the left frame
left_frame = ttk.Frame(window)
left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create the right frame
right_frame = ttk.Frame(window)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create a text area in the left frame
text_area = tk.Text(left_frame, width=30, height=10)
text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Increase the font size of the text area
text_font = font.Font(size=20)  # Adjust the font size as desired
text_area.configure(font=text_font, state='disabled')

# Create the start button
start_button = ttk.Button(left_frame, text="Start", command=start_detection)
start_button.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, pady=10)

# Create a label to display the OpenCV frame
image_label = ttk.Label(right_frame)
image_label.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Create the stop button
stop_button = ttk.Button(right_frame, text="Stop", command=stop_detection)
stop_button.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, pady=10)

# Start with the placeholder image
placeholder_image = ImageTk.PhotoImage(Image.new('RGB', (400, 400)))
image_label.configure(image=placeholder_image)
image_label.image = placeholder_image

# Start the GUI event loop
window.mainloop()