import numpy as np
from PIL import Image
from time import time
from time import sleep
import torch
import cv2
import serial
import os
import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter import messagebox
from PIL import ImageTk, Image
import csv
from datetime import datetime

ser = serial.Serial('COM14', 115200)
infrared = serial.Serial('COM4', 115200)

# Load the model
model = torch.hub.load('yolov5', 'custom', path='models/KelapaV3_YOLOv5.pt', source='local')

# Declare variables
get_datetime_file = datetime.now()
csv_file_path = "log/log_kelapa_{}.csv".format(get_datetime_file.strftime("%Y-%m-%d-%S"))
total_counter = 0
standar_counter = 0
nonStandar_counter = 0
notDefined_counter = 0

def show_alert(subject, message):
    messagebox.showinfo(subject, message)

def update_text(formatted_datetime, quality, accuracy, width, height, class_counter, total_counter):
    text_area.configure(state='normal')
    text_area.insert("end", "\n Time: {} \n Quality: {} \n Accuracy: {}% \n Width: {} cm \n Height: {} cm \n Class_Counter: {} \n Total_Counter: {} \n"
                     .format(formatted_datetime, quality, accuracy, width, height, class_counter, total_counter))
    text_area.configure(state='disabled')
    text_area.see("end")
    
def save_to_csv():
    # Get the current contents of the text_area widget
    text_contents = text_area.get("1.0", "end-1c")

    # Extract the values from the text contents
    lines = text_contents.split("\n")
    data = [line.split(": ")[1] for line in lines if line]

    # Define the header row and data rows
    header_row = ["Time", "Quality", "Accuracy", "Width", "Height", "Class_Counter", "Total_Counter"]
    data_rows = [data[i:i+7] for i in range(0, len(data), 7)] 
    
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname("log/"), exist_ok=True)

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
            # Resize the frame for compatibility (optional)
            #resized_frame = cv2.resize(frame, (640, 640))

            # Convert the frame to RGB format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Create an ImageTk object
            image_tk = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))

            # Update the label with the new image
            image_label.configure(image=image_tk)
            image_label.image = image_tk

            if (infrared.inWaiting() > 0):
                baca = infrared.readline()
                print(baca)
                if baca == b'OBSTACLE\r\n':
                    # Trigger 'OBSTACLE' from Serial
                    
                    # Create the directory if it doesn't exist
                    os.makedirs(os.path.dirname("capture_img/"), exist_ok=True)
                    # Automatically capture the frame
                    img_name = "capture_img/capture_img.jpg"
                    # Save the frame as an image file
                    cv2.imwrite(img_name, frame)
                    # Load the image file
                    results = model(img_name)
                    
                    # Save the predicted image
                    img_name_predicted = "capture_img_predicted"
                    results.save(save_dir=img_name_predicted, exist_ok=True)
                    
                    try:
                        # Get bounding box width and height
                        xyxy_df = results.pandas().xyxy[0]
                        xmin = xyxy_df['xmin'].values[0].astype(float)
                        ymin = xyxy_df['ymin'].values[0].astype(float)
                        xmax = xyxy_df['xmax'].values[0].astype(float)
                        ymax = xyxy_df['ymax'].values[0].astype(float)
                        accuracy = xyxy_df['confidence'].values[0].astype(float)

                        # Count the width and height
                        object_width = xmax - xmin
                        object_height = ymax - ymin
                        
                        # Convert pixel to cm
                        object_width = object_width * 0.026458
                        object_height = object_height * 0.026458
                        
                        # Convert accuracy to percentage
                        accuracy = accuracy * 100

                        # Round decimals
                        object_width = round(object_width, 2)
                        object_height = round(object_height, 2)
                        accuracy = round(accuracy, 2)
                    except:
                        object_width = 0
                        object_height = 0
                        accuracy = 0
                    
                    # Show it to the GUI
                    image_tk = ImageTk.PhotoImage(Image.open(img_name_predicted + "/capture_img.jpg"))
                    
                    # Update the label with the new image
                    image_label.configure(image=image_tk)
                    image_label.image = image_tk

                    # Get the current datetime
                    get_datetime_now = datetime.now()
                    # Format the datetime as desired
                    formatted_datetime = get_datetime_now.strftime("%Y-%m-%d-%S.%f")
                    
                    try:
                        check = results.pandas().xyxy[0].round(3).round(2)['name'][0]
                    except:
                        check = "NotDefined"
                        
                    if check == 'Standar':
                        quality = 'Standar'
                        standar_counter += 1
                        total_counter += 1
                        # Update the text area
                        update_text(formatted_datetime, quality, accuracy, object_width, object_height, standar_counter, total_counter)
                        # Save to CSV
                        save_to_csv()
                        # SERIAL ACTIONS
                        ser.write("r".encode())
                    elif check == 'NonStandar':
                        quality = 'NonStandar'
                        nonStandar_counter += 1
                        total_counter += 1
                        # Update the text area
                        update_text(formatted_datetime, quality, accuracy, object_width, object_height, nonStandar_counter, total_counter)
                        # Save to CSV
                        save_to_csv()
                        # SERIAL ACTIONS
                        ser.write("l".encode())
                    elif check == 'NotDefined':
                        # quality = 'NotDefined'
                        # notDefined_counter += 1
                        # total_counter += 1
                        # # Update the text area
                        # update_text(formatted_datetime, quality, accuracy, object_width, object_height, notDefined_counter, total_counter)
                        # # Save to CSV
                        # save_to_csv()
                        # # SERIAL ACTIONS
                        pass

            # Schedule the next frame update
            image_label.after(30, update_frame)
    else:
        # Display the placeholder image if no frame is available
        image_label.configure(image=placeholder_image)
        image_label.image = placeholder_image

def start_detection():
    global video_capture
    if video_capture is None:
        # Open the video capture device with the desired resolution
        video_capture = cv2.VideoCapture(2)  # Use 0 for the default camera
        
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
